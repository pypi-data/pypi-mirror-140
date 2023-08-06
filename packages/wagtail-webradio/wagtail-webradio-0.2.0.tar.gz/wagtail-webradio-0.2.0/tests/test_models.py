from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

import pytest

from wagtail_webradio.models import GroupRadioShowPermission

from .factories import PodcastFactory, RadioShowFactory


class TestAutoSlugMixin:
    def test_radioshow_slug(self):
        radioshow = RadioShowFactory.build(title="Ûnicode Show")
        assert radioshow.slug == ''

        radioshow.full_clean()
        radioshow.save()
        assert radioshow.slug == 'unicode-show'

    def test_poadcast_slug(self):
        podcast = PodcastFactory.build(
            title="Ûnicode Podcast", radio_show=RadioShowFactory()
        )
        assert podcast.slug == ''

        podcast.full_clean()
        podcast.save()
        assert podcast.slug == 'unicode-podcast'

    def test_generated_slug_update(self):
        radioshow = RadioShowFactory.build(title="A simple Show")
        radioshow.full_clean()
        radioshow.save()
        assert radioshow.slug == 'a-simple-show'

        radioshow.slug = ''
        radioshow.full_clean()
        radioshow.save()
        assert radioshow.slug == 'a-simple-show'

    def test_generated_slug_suffix(self):
        radioshow = RadioShowFactory.build(title="A simple Show")
        radioshow.full_clean()
        radioshow.save()
        assert radioshow.slug == 'a-simple-show'

        radioshow1 = RadioShowFactory.build(title="a Simple show")
        radioshow1.full_clean()
        assert radioshow1.slug == 'a-simple-show-1'

    def test_empty_base_slug(self):
        radioshow = RadioShowFactory.build(title="")

        with pytest.raises(ValidationError) as exc_info:
            radioshow.full_clean()
        assert set(exc_info.value.error_dict.keys()) == {'title', 'slug'}

    def test_slug_unavailable(self):
        RadioShowFactory(title="A simple Show")

        radioshow = RadioShowFactory.build(
            title="A simple Show", slug='a-simple-show'
        )
        with pytest.raises(ValidationError) as exc_info:
            radioshow.full_clean()
        assert set(exc_info.value.error_dict.keys()) == {'slug'}
        assert "already in use" in exc_info.value.messages[0]


class TestGroupRadioShowPermission:
    def test_natural_key(self, change_radioshow_perm):
        group = Group.objects.create(name="A group")
        radio_show = RadioShowFactory()

        obj = GroupRadioShowPermission.objects.create(
            group=group,
            radio_show=radio_show,
            permission=change_radioshow_perm,
        )

        assert obj.natural_key() == (group, radio_show, change_radioshow_perm)
        assert (
            GroupRadioShowPermission.objects.get_by_natural_key(
                group, radio_show, change_radioshow_perm
            )
            == obj
        )
