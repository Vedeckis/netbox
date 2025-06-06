from django.contrib.postgres.aggregates import JSONBAgg
from django.db.models import OuterRef, Subquery, Q

from extras.models.tags import TaggedItem
from utilities.query_functions import EmptyGroupByJSONBAgg
from utilities.querysets import RestrictedQuerySet

__all__ = (
    'ConfigContextModelQuerySet',
    'ConfigContextQuerySet',
    'NotificationQuerySet',
)


class ConfigContextQuerySet(RestrictedQuerySet):

    def get_for_object(self, obj, aggregate_data=False):
        """
        Return all applicable ConfigContexts for a given object. Only active ConfigContexts will be included.

        Args:
          aggregate_data: If True, use the JSONBAgg aggregate function to return only the list of JSON data objects
        """

        # Device type and location assignment is relevant only for Devices
        device_type = getattr(obj, 'device_type', None)
        location = getattr(obj, 'location', None)

        # Get assigned cluster, group, and type (if any)
        cluster = getattr(obj, 'cluster', None)
        cluster_type = getattr(cluster, 'type', None)
        cluster_group = getattr(cluster, 'group', None)

        # Get the group of the assigned tenant, if any
        tenant_group = obj.tenant.group if obj.tenant else None

        # Match against the directly assigned region as well as any parent regions.
        region = getattr(obj.site, 'region', None)
        regions = region.get_ancestors(include_self=True) if region else []

        # Match against the directly assigned site group as well as any parent site groups.
        sitegroup = getattr(obj.site, 'group', None)
        sitegroups = sitegroup.get_ancestors(include_self=True) if sitegroup else []

        # Match against the directly assigned role as well as any parent roles.
        device_roles = obj.role.get_ancestors(include_self=True) if obj.role else []

        queryset = self.filter(
            Q(regions__in=regions) | Q(regions=None),
            Q(site_groups__in=sitegroups) | Q(site_groups=None),
            Q(sites=obj.site) | Q(sites=None),
            Q(locations=location) | Q(locations=None),
            Q(device_types=device_type) | Q(device_types=None),
            Q(roles__in=device_roles) | Q(roles=None),
            Q(platforms=obj.platform) | Q(platforms=None),
            Q(cluster_types=cluster_type) | Q(cluster_types=None),
            Q(cluster_groups=cluster_group) | Q(cluster_groups=None),
            Q(clusters=cluster) | Q(clusters=None),
            Q(tenant_groups=tenant_group) | Q(tenant_groups=None),
            Q(tenants=obj.tenant) | Q(tenants=None),
            Q(tags__slug__in=obj.tags.slugs()) | Q(tags=None),
            is_active=True,
        ).order_by('weight', 'name').distinct()

        if aggregate_data:
            return queryset.aggregate(
                config_context_data=JSONBAgg('data', ordering=['weight', 'name'])
            )['config_context_data']

        return queryset


class ConfigContextModelQuerySet(RestrictedQuerySet):
    """
    QuerySet manager used by models which support ConfigContext (device and virtual machine).

    Includes a method which appends an annotation of aggregated config context JSON data objects. This is
    implemented as a subquery which performs all the joins necessary to filter relevant config context objects.
    This offers a substantial performance gain over ConfigContextQuerySet.get_for_object() when dealing with
    multiple objects. This allows the annotation to be entirely optional.
    """
    def annotate_config_context_data(self):
        """
        Attach the subquery annotation to the base queryset
        """
        from extras.models import ConfigContext
        return self.annotate(
            config_context_data=Subquery(
                ConfigContext.objects.filter(
                    self._get_config_context_filters()
                ).annotate(
                    _data=EmptyGroupByJSONBAgg('data', ordering=['weight', 'name'])
                ).values("_data").order_by()
            )
        ).distinct()

    def _get_config_context_filters(self):
        # Construct the set of Q objects for the specific object types
        tag_query_filters = {
            "object_id": OuterRef(OuterRef('pk')),
            "content_type__app_label": self.model._meta.app_label,
            "content_type__model": self.model._meta.model_name
        }
        base_query = Q(
            Q(platforms=OuterRef('platform')) | Q(platforms=None),
            Q(cluster_types=OuterRef('cluster__type')) | Q(cluster_types=None),
            Q(cluster_groups=OuterRef('cluster__group')) | Q(cluster_groups=None),
            Q(clusters=OuterRef('cluster')) | Q(clusters=None),
            Q(tenant_groups=OuterRef('tenant__group')) | Q(tenant_groups=None),
            Q(tenants=OuterRef('tenant')) | Q(tenants=None),
            Q(sites=OuterRef('site')) | Q(sites=None),
            Q(
                tags__pk__in=Subquery(
                    TaggedItem.objects.filter(
                        **tag_query_filters
                    ).values_list(
                        'tag_id',
                        flat=True
                    )
                )
            ) | Q(tags=None),
            is_active=True,
        )

        # Apply Location & DeviceType filters only for VirtualMachines
        if self.model._meta.model_name == 'device':
            base_query.add((Q(locations=OuterRef('location')) | Q(locations=None)), Q.AND)
            base_query.add((Q(device_types=OuterRef('device_type')) | Q(device_types=None)), Q.AND)
        elif self.model._meta.model_name == 'virtualmachine':
            base_query.add(Q(locations=None), Q.AND)
            base_query.add(Q(device_types=None), Q.AND)

        # MPTT-based filters
        base_query.add(
            (Q(
                regions__tree_id=OuterRef('site__region__tree_id'),
                regions__level__lte=OuterRef('site__region__level'),
                regions__lft__lte=OuterRef('site__region__lft'),
                regions__rght__gte=OuterRef('site__region__rght'),
            ) | Q(regions=None)),
            Q.AND
        )
        base_query.add(
            (Q(
                site_groups__tree_id=OuterRef('site__group__tree_id'),
                site_groups__level__lte=OuterRef('site__group__level'),
                site_groups__lft__lte=OuterRef('site__group__lft'),
                site_groups__rght__gte=OuterRef('site__group__rght'),
            ) | Q(site_groups=None)),
            Q.AND
        )
        base_query.add(
            (Q(
                roles__tree_id=OuterRef('role__tree_id'),
                roles__level__lte=OuterRef('role__level'),
                roles__lft__lte=OuterRef('role__lft'),
                roles__rght__gte=OuterRef('role__rght'),
            ) | Q(roles=None)),
            Q.AND
        )

        return base_query


class NotificationQuerySet(RestrictedQuerySet):

    def unread(self):
        """
        Return only unread notifications.
        """
        return self.filter(read__isnull=True)
