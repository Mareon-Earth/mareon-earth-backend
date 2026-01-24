import logging
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users.schemas import UserCreate, UserUpdate
from app.domain.users.repository import UserRepository
from app.domain.organization.schemas import OrganizationCreate, OrganizationUpdate
from app.domain.organization.models import OrganizationRole
from app.services.user_service import UserService
from app.services.organization_service import OrganizationService

logger = logging.getLogger(__name__)

user_service = UserService(user_repository=UserRepository())
org_service = OrganizationService()


class WebhookHandlers:
    """
    Handlers for Clerk webhook events.
    Each handler syncs Clerk data to local database.
    """

    @staticmethod
    async def handle_user_created(db: AsyncSession, data: Dict[str, Any]) -> None:
        """
        Handle user.created event.
        Creates local user record synced with Clerk.
        The service will automatically sync the internal user_id back to Clerk metadata.
        """
        try:
            payload = UserCreate(
                clerk_user_id=data["id"],
                email=data["email_addresses"][0]["email_address"],
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                full_name=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or None,
                image_url=data.get("image_url"),
            )
            await user_service.get_or_create_from_clerk(db, payload)
            logger.info(f"User created: {data['id']}")
        except Exception as e:
            logger.error(f"Failed to handle user.created: {e}", exc_info=True)
            raise

    @staticmethod
    async def handle_user_updated(db: AsyncSession, data: Dict[str, Any]) -> None:
        """
        Handle user.updated event.
        Updates local user record with Clerk changes.
        """
        try:
            payload = UserUpdate(
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                full_name=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or None,
                image_url=data.get("image_url"),
            )
            await user_service.update_user(db, data["id"], payload)
            logger.info(f"User updated: {data['id']}")
        except Exception as e:
            logger.error(f"Failed to handle user.updated: {e}", exc_info=True)
            raise

    @staticmethod
    async def handle_user_deleted(db: AsyncSession, data: Dict[str, Any]) -> None:
        """
        Handle user.deleted event.
        Deletes user from local database when deleted in Clerk.
        """
        try:
            await user_service.delete_user(db, data["id"])
            logger.info(f"User deleted: {data['id']}")
        except Exception as e:
            logger.error(f"Failed to handle user.deleted: {e}", exc_info=True)
            raise

    @staticmethod
    async def handle_organization_created(db: AsyncSession, data: Dict[str, Any]) -> None:
        """
        Handle organization.created event.
        Creates local organization record synced with Clerk.
        The service will automatically sync the internal org_id back to Clerk metadata.
        """
        try:
            payload = OrganizationCreate(
                clerk_id=data["id"],
                name=data["name"],
                logo_url=data.get("logo_url"),
            )
            await org_service.get_or_create_from_clerk(db, payload)
            logger.info(f"Organization created: {data['id']}")
        except Exception as e:
            logger.error(f"Failed to handle organization.created: {e}", exc_info=True)
            raise

    @staticmethod
    async def handle_organization_updated(db: AsyncSession, data: Dict[str, Any]) -> None:
        """
        Handle organization.updated event.
        Updates local organization record with Clerk changes.
        """
        try:
            payload = OrganizationUpdate(
                name=data.get("name"),
                logo_url=data.get("logo_url"),
            )
            await org_service.update_organization(db, data["id"], payload)
            logger.info(f"Organization updated: {data['id']}")
        except Exception as e:
            logger.error(f"Failed to handle organization.updated: {e}", exc_info=True)
            raise

    @staticmethod
    async def handle_organization_deleted(db: AsyncSession, data: Dict[str, Any]) -> None:
        """
        Handle organization.deleted event.
        Removes local organization record (cascades to members).
        """
        try:
            await org_service.delete_organization(db, data["id"])
            logger.info(f"Organization deleted: {data['id']}")
        except Exception as e:
            logger.error(f"Failed to handle organization.deleted: {e}", exc_info=True)
            raise

    @staticmethod
    async def handle_organization_membership_created(
        db: AsyncSession, data: Dict[str, Any]
    ) -> None:
        """
        Handle organizationMembership.created event.
        Adds user to organization with appropriate role.
        Both user and org will have their internal IDs synced to Clerk if newly created.
        """
        try:
            # Map Clerk roles to internal OrgRole enum
            clerk_role = data.get("role", "basic_member")
            role = WebhookHandlers._map_clerk_role(clerk_role)

            # Ensure user exists (get or create from webhook data)
            # This will sync user_id to Clerk if newly created
            user_payload = UserCreate(
                clerk_user_id=data["public_user_data"]["user_id"],
                email=data["public_user_data"].get("identifier", ""),
                first_name=data["public_user_data"].get("first_name"),
                last_name=data["public_user_data"].get("last_name"),
                full_name=f"{data['public_user_data'].get('first_name', '')} {data['public_user_data'].get('last_name', '')}".strip() or None,
            )
            user = await user_service.get_or_create_from_clerk(db, user_payload)

            # Ensure organization exists (get or create from webhook data)
            # This will sync org_id to Clerk if newly created
            org_payload = OrganizationCreate(
                clerk_id=data["organization"]["id"],
                name=data["organization"]["name"],
                logo_url=data["organization"].get("logo_url"),
            )
            org = await org_service.get_or_create_from_clerk(db, org_payload)

            await org_service.add_member(db, user.id, org.id, role)
            logger.info(
                f"Member added: user={data['public_user_data']['user_id']}, "
                f"org={data['organization']['id']}, role={role}"
            )
        except Exception as e:
            logger.error(
                f"Failed to handle organizationMembership.created: {e}", exc_info=True
            )
            raise

    @staticmethod
    async def handle_organization_membership_updated(
        db: AsyncSession, data: Dict[str, Any]
    ) -> None:
        """
        Handle organizationMembership.updated event.
        Updates member role in organization.
        """
        try:
            clerk_role = data.get("role", "basic_member")
            role = WebhookHandlers._map_clerk_role(clerk_role)

            # Ensure user exists
            user_payload = UserCreate(
                clerk_user_id=data["public_user_data"]["user_id"],
                email=data["public_user_data"].get("identifier", ""),
                first_name=data["public_user_data"].get("first_name"),
                last_name=data["public_user_data"].get("last_name"),
                full_name=f"{data['public_user_data'].get('first_name', '')} {data['public_user_data'].get('last_name', '')}".strip() or None,
            )
            user = await user_service.get_or_create_from_clerk(db, user_payload)

            # Ensure organization exists
            org_payload = OrganizationCreate(
                clerk_id=data["organization"]["id"],
                name=data["organization"]["name"],
                logo_url=data["organization"].get("logo_url"),
            )
            org = await org_service.get_or_create_from_clerk(db, org_payload)

            await org_service.update_member_role(db, user.id, org.id, role)
            logger.info(
                f"Member updated: user={data['public_user_data']['user_id']}, "
                f"org={data['organization']['id']}, new_role={role}"
            )
        except Exception as e:
            logger.error(
                f"Failed to handle organizationMembership.updated: {e}", exc_info=True
            )
            raise

    @staticmethod
    async def handle_organization_membership_deleted(
        db: AsyncSession, data: Dict[str, Any]
    ) -> None:
        """
        Handle organizationMembership.deleted event.
        Removes user from organization.
        """
        try:
            # For deletion, we expect both user and org to exist
            user = await user_service.get_user_by_clerk_id(db, data["public_user_data"]["user_id"])
            org = await org_service.get_organization(db, data["organization"]["id"])

            await org_service.remove_member(db, user.id, org.id)
            logger.info(
                f"Member removed: user={data['public_user_data']['user_id']}, "
                f"org={data['organization']['id']}"
            )
        except Exception as e:
            logger.error(
                f"Failed to handle organizationMembership.deleted: {e}", exc_info=True
            )
            raise

    @staticmethod
    def _map_clerk_role(clerk_role: str) -> OrganizationRole:
        """
        Map Clerk organization roles to internal OrgRole enum.
        Clerk roles: org:admin, org:member, basic_member, admin, etc.
        """
        role_lower = clerk_role.lower()
        
        if "admin" in role_lower:
            return OrganizationRole.ADMIN
        elif role_lower in ("org:owner", "owner"):
            return OrganizationRole.OWNER
        else:
            return OrganizationRole.MEMBER


async def dispatch_webhook_event(
    event_type: str, data: Dict[str, Any], db: AsyncSession
) -> None:
    """
    Route webhook events to appropriate handlers.
    """
    handlers = {
        "user.created": WebhookHandlers.handle_user_created,
        "user.updated": WebhookHandlers.handle_user_updated,
        "user.deleted": WebhookHandlers.handle_user_deleted,
        "organization.created": WebhookHandlers.handle_organization_created,
        "organization.updated": WebhookHandlers.handle_organization_updated,
        "organization.deleted": WebhookHandlers.handle_organization_deleted,
        "organizationMembership.created": WebhookHandlers.handle_organization_membership_created,
        "organizationMembership.updated": WebhookHandlers.handle_organization_membership_updated,
        "organizationMembership.deleted": WebhookHandlers.handle_organization_membership_deleted,
    }

    handler = handlers.get(event_type)
    if handler:
        await handler(db, data)
    else:
        logger.warning(f"No handler for event type: {event_type}")