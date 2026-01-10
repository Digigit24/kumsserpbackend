"""Seed organizational hierarchy based on org chart."""
from django.core.management.base import BaseCommand
from apps.core.models import OrganizationNode, DynamicRole, College


class Command(BaseCommand):
    help = 'Seed organizational hierarchy structure'

    def add_arguments(self, parser):
        parser.add_argument('--college-id', type=int, help='College ID to assign nodes to')

    def handle(self, *args, **options):
        college_id = options.get('college_id')
        college = None
        if college_id:
            try:
                college = College.objects.get(id=college_id)
            except College.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'College with ID {college_id} not found'))
                return

        # Create CEO (root)
        ceo, _ = OrganizationNode.objects.get_or_create(
            name='CEO',
            node_type='ceo',
            defaults={'college': college, 'order': 1, 'is_active': True}
        )

        # Level 1 - Direct reports to CEO
        nodes_level_1 = [
            ('ITI Principal', 'iti_principal', 1),
            ('Principals Parallel', 'principal_parallel', 2),
            ('Construction And', 'construction', 3),
            ('Central Store', 'central_store', 4),
            ('SPMM Principal', 'spmm_principal', 5),
            ('PSK', 'psk', 6),
        ]

        for name, node_type, order in nodes_level_1:
            OrganizationNode.objects.get_or_create(
                name=name,
                node_type=node_type,
                parent=ceo,
                defaults={'college': college, 'order': order, 'is_active': True}
            )

        # ITI Principal children
        iti = OrganizationNode.objects.get(name='ITI Principal')
        iti_children = [
            ('Viceprincipal/Super', 'viceprincipal_super', 1),
            ('Store Manager', 'store_manager', 2),
            ('Clerk', 'clerk', 3),
            ('Accountant', 'accountant', 4),
            ('Librarian', 'librarian', 5),
            ('Admission and', 'admission', 6),
            ('Hostel Incharge', 'hostel_incharge', 7),
        ]

        for name, node_type, order in iti_children:
            OrganizationNode.objects.get_or_create(
                name=name,
                node_type=node_type,
                parent=iti,
                defaults={'college': college, 'order': order, 'is_active': True}
            )

        # Viceprincipal/Super child
        vp = OrganizationNode.objects.get(name='Viceprincipal/Super')
        OrganizationNode.objects.get_or_create(
            name='Teacher/Trade',
            node_type='teacher',
            parent=vp,
            defaults={'college': college, 'order': 1, 'is_active': True}
        )

        # Admission and children
        admission = OrganizationNode.objects.get(name='Admission and')
        admission_children = [
            ('Telecaller', 'telecaller', 1),
        ]
        for name, node_type, order in admission_children:
            OrganizationNode.objects.get_or_create(
                name=name,
                node_type=node_type,
                parent=admission,
                defaults={'college': college, 'order': order, 'is_active': True}
            )

        # Hostel Incharge children
        hostel = OrganizationNode.objects.get(name='Hostel Incharge')
        hostel_children = [
            ('Hostel Rector', 'hostel_rector', 1),
            ('Mess/Canteen', 'mess_canteen', 2),
        ]
        for name, node_type, order in hostel_children:
            OrganizationNode.objects.get_or_create(
                name=name,
                node_type=node_type,
                parent=hostel,
                defaults={'college': college, 'order': order, 'is_active': True}
            )

        # Central Store children
        central = OrganizationNode.objects.get(name='Central Store')
        OrganizationNode.objects.get_or_create(
            name='Jr Engineer',
            node_type='jr_engineer',
            parent=central,
            defaults={'college': college, 'order': 1, 'is_active': True}
        )

        # SPMM Principal children
        spmm = OrganizationNode.objects.get(name='SPMM Principal')
        spmm_children = [
            ('Viceprincipal', 'viceprincipal', 1),
            ('Store', 'store', 2),
        ]
        for name, node_type, order in spmm_children:
            OrganizationNode.objects.get_or_create(
                name=name,
                node_type=node_type,
                parent=spmm,
                defaults={'college': college, 'order': order, 'is_active': True}
            )

        # Viceprincipal (SPMM) children
        vp_spmm = OrganizationNode.objects.filter(name='Viceprincipal', parent=spmm).first()
        if vp_spmm:
            vp_children = [
                ('Professor', 'professor', 1),
                ('Associate Professor', 'associate_professor', 2),
                ('Assistant Professor', 'assistant_professor', 3),
            ]
            for name, node_type, order in vp_children:
                OrganizationNode.objects.get_or_create(
                    name=name,
                    node_type=node_type,
                    parent=vp_spmm,
                    defaults={'college': college, 'order': order, 'is_active': True}
                )

        # PSK children
        psk = OrganizationNode.objects.get(name='PSK')
        psk_children = [
            ('Viceprincipal', 'viceprincipal', 1),
            ('Lab Assistant', 'lab_assistant', 2),
            ('Clerk', 'clerk', 3),
            ('Accountant', 'accountant', 4),
            ('Librarian', 'librarian', 5),
        ]
        for name, node_type, order in psk_children:
            node, created = OrganizationNode.objects.get_or_create(
                name=name,
                node_type=node_type,
                parent=psk,
                defaults={'college': college, 'order': order, 'is_active': True}
            )

        count = OrganizationNode.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Successfully created org hierarchy with {count} nodes'))
