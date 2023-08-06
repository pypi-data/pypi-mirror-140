from unittest.mock import patch

from django.contrib.admin.sites import AdminSite
from django.test import RequestFactory, TestCase
from django.urls import reverse

from ..admin import CharacterAdmin, SkillSetAdmin, SkillSetShipTypeFilter
from ..models import Character, EveShipType, SkillSet
from .testdata.factories import create_character_update_status
from .testdata.load_entities import load_entities
from .testdata.load_eveuniverse import load_eveuniverse
from .utils import (
    create_memberaudit_character,
    create_user_from_evecharacter_with_access,
)

ADMIN_PATH = "memberaudit.admin"


class MockRequest(object):
    def __init__(self, user=None, post=None):
        self.user = user
        self.POST = post

    def get_full_path(self):
        return "/dummy-full-path"


class TestCharacterAdmin(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.modeladmin = CharacterAdmin(model=Character, admin_site=AdminSite())
        load_eveuniverse()
        load_entities()
        cls.character = create_memberaudit_character(1001)
        cls.user = cls.character.character_ownership.user

    def test_column_character(self):
        self.assertEqual(self.modeladmin._character(self.character), "Bruce Wayne")

    def test_column_main_normal(self):
        self.assertEqual(self.modeladmin._main(self.character), "Bruce Wayne")

    def test_column_main_no_main(self):
        # given
        character = create_memberaudit_character(1002)
        user = character.character_ownership.user
        user.profile.main_character = None
        user.profile.save()
        # when
        self.assertIsNone(self.modeladmin._main(character))

    def test_column_state(self):
        self.assertEqual(self.modeladmin._state(self.character), "Guest")

    def test_column_organization_normal(self):
        self.assertEqual(
            self.modeladmin._organization(self.character), "Wayne Technologies [WYN]"
        )

    def test_column_organization_no_main(self):
        # given
        character = create_memberaudit_character(1002)
        user = character.character_ownership.user
        user.profile.main_character = None
        user.profile.save()
        # when
        self.assertIsNone(self.modeladmin._organization(character))

    def test_column_missing_sections_none(self):
        # given
        for section in Character.UpdateSection:
            create_character_update_status(character=self.character, section=section)
        self.assertIsNone(self.modeladmin._missing_sections(self.character))

    def test_column_missing_sections_two_missing(self):
        # given
        sections = [
            obj
            for obj in Character.UpdateSection
            if obj is not Character.UpdateSection.ASSETS
            and obj is not Character.UpdateSection.CONTRACTS
        ]
        for section in sections:
            create_character_update_status(character=self.character, section=section)
        self.assertListEqual(
            self.modeladmin._missing_sections(self.character), ["assets", "contracts"]
        )

    @patch(ADMIN_PATH + ".CharacterAdmin.message_user")
    @patch(ADMIN_PATH + ".tasks.update_character")
    def test_should_update_characters(
        self, mock_task_update_character, mock_message_user
    ):
        # given
        request = MockRequest(user=self.user)
        queryset = Character.objects.all()
        # when
        self.modeladmin.update_characters(request, queryset)
        # then
        self.assertEqual(mock_task_update_character.delay.call_count, 1)
        self.assertTrue(mock_message_user.called)

    @patch(ADMIN_PATH + ".CharacterAdmin.message_user")
    @patch(ADMIN_PATH + ".tasks.delete_character")
    def test_should_delete_characters_1(
        self, mock_task_delete_character, mock_message_user
    ):
        # given
        factory = RequestFactory()
        request = factory.get(reverse("admin:memberaudit_character_changelist"))
        queryset = Character.objects.all()
        # when
        response = self.modeladmin.delete_characters(request, queryset)
        # then
        self.assertEqual(response.status_code, 200)

    @patch(ADMIN_PATH + ".CharacterAdmin.message_user")
    @patch(ADMIN_PATH + ".tasks.delete_character")
    def test_should_delete_characters_2(
        self, mock_task_delete_character, mock_message_user
    ):
        # given
        request = MockRequest(user=self.user, post="apply")
        queryset = Character.objects.all()
        # when
        self.modeladmin.delete_characters(request, queryset)
        # then
        self.assertEqual(mock_task_delete_character.delay.call_count, 1)
        self.assertTrue(mock_message_user.called)


class TestSkillSetAdmin(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factory = RequestFactory()
        cls.modeladmin = SkillSetAdmin(model=SkillSet, admin_site=AdminSite())
        load_eveuniverse()
        load_entities()
        cls.user, _ = create_user_from_evecharacter_with_access(1001)

    @patch(ADMIN_PATH + ".tasks.update_characters_skill_checks")
    def test_save_model(self, mock_update_characters_skill_checks):
        ship = SkillSet.objects.create(name="Dummy")
        request = MockRequest(self.user)
        form = self.modeladmin.get_form(request)
        self.modeladmin.save_model(request, ship, form, True)

        self.assertTrue(mock_update_characters_skill_checks.delay.called)

    @patch(ADMIN_PATH + ".tasks.update_characters_skill_checks")
    def test_delete_model(self, mock_update_characters_skill_checks):
        ship = SkillSet.objects.create(name="Dummy")
        request = MockRequest(self.user)
        self.modeladmin.delete_model(request, ship)

        self.assertTrue(mock_update_characters_skill_checks.delay.called)

    def test_ship_type_filter(self):
        class SkillSetAdminTest(SkillSetAdmin):
            list_filter = (SkillSetShipTypeFilter,)

        my_modeladmin = SkillSetAdminTest(SkillSet, AdminSite())

        ss_1 = SkillSet.objects.create(name="Set 1")
        ss_2 = SkillSet.objects.create(
            name="Set 2", ship_type=EveShipType.objects.get(id=603)
        )

        # Make sure the lookups are correct
        request = self.factory.get("/")
        request.user = self.user
        changelist = my_modeladmin.get_changelist_instance(request)
        filters = changelist.get_filters(request)
        filterspec = filters[0][0]
        expected = [("yes", "yes"), ("no", "no")]
        self.assertEqual(filterspec.lookup_choices, expected)

        # Make sure the correct queryset is returned
        request = self.factory.get("/", {"is_ship_type": "yes"})
        request.user = self.user
        changelist = my_modeladmin.get_changelist_instance(request)
        queryset = changelist.get_queryset(request)
        expected = {ss_2}
        self.assertSetEqual(set(queryset), expected)

        # Make sure the correct queryset is returned
        request = self.factory.get("/", {"is_ship_type": "no"})
        request.user = self.user
        changelist = my_modeladmin.get_changelist_instance(request)
        queryset = changelist.get_queryset(request)
        expected = {ss_1}
        self.assertSetEqual(set(queryset), expected)
