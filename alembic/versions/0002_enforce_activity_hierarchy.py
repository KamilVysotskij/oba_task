"""enforce activity hierarchy

Revision ID: 0002_enforce_activity_hierarchy
Revises: 0001_initial_schema
Create Date: 2026-03-18 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0002_enforce_activity_hierarchy'
down_revision: str | Sequence[str] | None = '0001_initial_schema'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION validate_activity_hierarchy()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        DECLARE
            total_activities integer;
            reachable_activities integer;
            max_depth integer;
            invalid_level_count integer;
        BEGIN
            WITH RECURSIVE activity_tree AS (
                SELECT
                    activities.id,
                    activities.parent_id,
                    activities.level,
                    1 AS depth,
                    ARRAY[activities.id] AS path
                FROM activities
                WHERE activities.parent_id IS NULL

                UNION ALL

                SELECT
                    child.id,
                    child.parent_id,
                    child.level,
                    activity_tree.depth + 1 AS depth,
                    activity_tree.path || child.id
                FROM activities AS child
                JOIN activity_tree ON child.parent_id = activity_tree.id
                WHERE array_position(activity_tree.path, child.id) IS NULL
            )
            SELECT
                (SELECT count(*) FROM activities),
                count(DISTINCT activity_tree.id),
                COALESCE(max(activity_tree.depth), 0),
                count(*) FILTER (
                    WHERE activity_tree.level <> activity_tree.depth
                )
            INTO
                total_activities,
                reachable_activities,
                max_depth,
                invalid_level_count
            FROM activity_tree;

            IF reachable_activities <> total_activities THEN
                RAISE EXCEPTION
                    'Activity hierarchy must be acyclic and connected '
                    'to a root activity.';
            END IF;

            IF max_depth > 3 THEN
                RAISE EXCEPTION
                    'Activity hierarchy depth cannot exceed 3 levels.';
            END IF;

            IF invalid_level_count > 0 THEN
                RAISE EXCEPTION
                    'Activity level must match its depth in the hierarchy.';
            END IF;

            RETURN NULL;
        END;
        $$;
        """
    )
    op.execute(
        """
        CREATE CONSTRAINT TRIGGER trg_validate_activity_hierarchy
        AFTER INSERT OR UPDATE OF parent_id, level OR DELETE
        ON activities
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW
        EXECUTE FUNCTION validate_activity_hierarchy();
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_validate_activity_hierarchy
        ON activities;
        """
    )
    op.execute(
        """
        DROP FUNCTION IF EXISTS validate_activity_hierarchy();
        """
    )
