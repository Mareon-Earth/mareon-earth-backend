import logging
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users.schemas import UserCreate, UserUpdate
from app.domain.users.dependencies import build_user_service
from app.domain.organization.schemas import OrganizationCreate, OrganizationUpdate
from app.domain.organization.models import OrganizationRole
from app.domain.organization.dependencies import build_organization_service

logger = logging.getLogger(__name__)

class WebhookHandlers:
    @staticmethod
    async def handle_user_created(db: AsyncSession, data: Dict[str, Any]) -> None:
        try:
            user_svc = build_user_service(db=db)
            payload = UserCreate(
                clerk_user_id=data["id"],
                email=data["email_addresses"][0]["email_address"],
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                full_name=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or None,
                image_url=data.get("image_url"),
            )
            await user_svc.create_user(payload)
            logger.info(f"User created: {data['id']}")
        except Exception as e:
            logger.error(f"Failed to handle user.created: {e}", exc_info=True)
            raise

    @staticmethod
    async def handle_user_updated(db: AsyncSession, data: Dict[str, Any]) -> None:
        try:
            user_svc = build_user_service(db=db)
            payload = UserUpdate(
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                full_name=f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or None,
                image_url=data.get("image_url"),
            )
            await user_svc.update_user_by_clerk_id(data["id"], payload)
            logger.info(f"User updated: {data['id']}")
        except Exception as e:
            logger.error(f"Failed to handle user.updated: {e}", exc_info=True)
            raise

    @staticmethod
    async def handle_user_deleted(db: AsyncSession, data: Dict[str, Any]) -> None:
        try:
            user_svc = build_user_service(db=db)
            await user_svc.delete_user_by_clerk_id(data["id"])
            logger.info(f"User deleted: {data['id']}")
        except Exception as e:
            logger.error(f"Failed to handle user.deleted: {e}", exc_info=True)
            raise

    @staticmethod
    async def handle_organization_created(db: AsyncSession, data: Dict[str, Any]) -> None:
        try:
            org_svc = build_organization_service(db=db)
            payload = OrganizationCreate(
                clerk_id=data["id"],
                name=data["name"],
                logo_url=data.get("logo_url"),
            )
            await org_svc.create_organization(payload)
            logger.info(f"Organization created: {data['id']}")
        except Exception as e:
            logger.error(f"Failed to handle organization.created: {e}", exc_info=True)
            raise

    @staticmethod
    async def handle_organization_updated(db: AsyncSession, data: Dict[str, Any]) -> None:
        try:
            org_svc = build_organization_service(db=db)
            org = await org_svc.get_organization_by_clerk_id(data["id"])
            payload = OrganizationUpdate(
                name=data.get("name"),
                logo_url=data.get("logo_url"),
            )
            await org_svc.update_organization(org.id, payload)
            logger.info(f"Organization updated: {data['id']}")
        except Exception as e:
            logger.error(f"Failed to handle organization.updated: {e}", exc_info=True)
            raise

    @staticmethod
    async def handle_organization_deleted(db: AsyncSession, data: Dict[str, Any]) -> None:
        try:
            org_svc = build_organization_service(db=db)
            org = await org_svc.get_organization_by_clerk_id(data["id"])
            await org_svc.delete_organization(org.id)
            logger.info(f"Organization deleted: {data['id']}")
        except Exception as e:
            logger.error(f"Failed to handle organization.deleted: {e}", exc_info=True)
            raise

    @staticmethod
    async def handle_organization_membership_created(
        db: AsyncSession, data: Dict[str, Any]
    ) -> None:
        try:
            user_svc = build_user_service(db=db)
            org_svc = build_organization_service(db=db)

            clerk_role = data.get("role", "basic_member")
            role = WebhookHandlers._map_clerk_role(clerk_role)

            user_payload = UserCreate(
                clerk_user_id=data["public_user_data"]["user_id"],
                email=data["public_user_data"].get("identifier", ""),
                first_name=data["public_user_data"].get("first_name"),
                last_name=data["public_user_data"].get("last_name"),
                full_name=f"{data['public_user_data'].get('first_name', '')} {data['public_user_data'].get('last_name', '')}".strip() or None,
            )

            try:
                user = await user_svc.get_user_by_clerk_id(data["public_user_data"]["user_id"])
            except Exception:
                user = await user_svc.create_user(user_payload)

            org_payload = OrganizationCreate(
                clerk_id=data["organization"]["id"],
                name=data["organization"]["name"],
                logo_url=data["organization"].get("logo_url"),
            )

            try:
                org = await org_svc.get_organization_by_clerk_id(data["organization"]["id"])
            except Exception:
                org = await org_svc.create_organization(org_payload)

            await org_svc.add_member_to_organization(org.id, user.id, role)
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
        try:
            user_svc = build_user_service(db=db)
            org_svc = build_organization_service(db=db)

            clerk_role = data.get("role", "basic_member")
            role = WebhookHandlers._map_clerk_role(clerk_role)

            user = await user_svc.get_user_by_clerk_id(data["public_user_data"]["user_id"])
            org = await org_svc.get_organization_by_clerk_id(data["organization"]["id"])

            await org_svc.update_organization_member_role(org.id, user.id, role)
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
        try:
            user_svc = build_user_service(db=db)
            org_svc = build_organization_service(db=db)

            user = await user_svc.get_user_by_clerk_id(data["public_user_data"]["user_id"])
            org = await org_svc.get_organization_by_clerk_id(data["organization"]["id"])

            await org_svc.remove_member_from_organization(org.id, user.id)
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