from abc import ABC, abstractmethod
from src.domain.model.group import Group
from typing import Optional
from uuid import UUID


class GroupRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: UUID) -> Optional[Group]:
        pass

    @abstractmethod
    def add(self, group: Group) -> Optional[Group]:
        pass

    @abstractmethod
    def delete(self, id: UUID) -> None:
        pass

    @abstractmethod
    def update(self, group: Group) -> Optional[Group]:
        pass

    @abstractmethod
    def add_member(self, group_id: UUID, user_id: UUID) -> None:
        pass

    @abstractmethod
    def remove_member(self, group_id: UUID, user_id: UUID) -> None:
        pass

    @abstractmethod
    def find_by_owner_id(self, owner_id: UUID) -> Optional[list[Group]]:
        pass

    @abstractmethod
    def list_members(self, group_id: UUID) -> Optional[list[UUID]]:
        pass

    @abstractmethod
    def find_all_groups(self) -> Optional[list[Group]]:
        pass