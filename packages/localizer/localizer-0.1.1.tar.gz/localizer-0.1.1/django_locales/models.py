from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


# Create your models here.


class Group(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name=_("group.name"),
    )

    class Meta:
        verbose_name = _("group.verbose")
        verbose_name_plural = _("group.plural")

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<Group pk={self.pk}>"


class GroupItem(models.Model):
    group = models.ForeignKey(
        to="django_locales.Group",
        on_delete=models.PROTECT,
        related_name="items",
        verbose_name=_("group.verbose"),
    )
    language = models.CharField(
        max_length=32,
        choices=settings.LANGUAGES,
        verbose_name=_("group_item.language"),
    )
    key = models.CharField(
        max_length=256,
        verbose_name=_("group_item.key"),
    )
    translate = models.CharField(
        max_length=256,
        verbose_name=_("group_item.translate"),
    )

    class Meta:
        verbose_name = _("group_item.verbose")
        verbose_name_plural = _("group_item.plural")
        constraints = (
            models.UniqueConstraint(
                fields=("language", "key"),
                name="unique_key",
            ),
        )

    def __str__(self) -> str:
        return f"{self.language}: {self.key}"

    def __repr__(self) -> str:
        return f"<GroupItem pk={self.pk}>"
