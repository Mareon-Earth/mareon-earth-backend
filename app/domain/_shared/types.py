from typing import TypeAlias

UserId: TypeAlias = str
OrganizationId: TypeAlias = str
DocumentId: TypeAlias = str
DocumentFileId: TypeAlias = str

OrganizationMemberId: TypeAlias = tuple[str, str]

ClerkUserId: TypeAlias = str
ClerkOrganizationId: TypeAlias = str
StoragePath: TypeAlias = str