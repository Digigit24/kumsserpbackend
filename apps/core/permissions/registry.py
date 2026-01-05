"""
Central registry of all resources and their available actions.
Add new resources here when creating new apps/features.
"""

PERMISSION_REGISTRY = {
    'attendance': {
        'actions': ['create', 'read', 'update', 'delete', 'export'],
        'description': 'Student attendance management',
    },
    'students': {
        'actions': ['create', 'read', 'update', 'delete', 'import', 'export'],
        'description': 'Student records management',
    },
    'classes': {
        'actions': ['create', 'read', 'update', 'delete', 'export'],
        'description': 'Class/section management',
    },
    'subjects': {
        'actions': ['create', 'read', 'update', 'delete', 'export'],
        'description': 'Subject management',
    },
    'fees': {
        'actions': ['create', 'read', 'update', 'delete', 'generate_invoice', 'export'],
        'description': 'Fee management',
    },
    'examinations': {
        'actions': ['create', 'read', 'update', 'delete', 'publish_results', 'export'],
        'description': 'Examination and results management',
    },
    'library': {
        'actions': ['create', 'read', 'update', 'delete', 'issue_book', 'return_book', 'export'],
        'description': 'Library management',
    },
    'hr': {
        'actions': ['create', 'read', 'update', 'delete', 'export'],
        'description': 'Human resources management',
    },
    'hostel': {
        'actions': ['create', 'read', 'update', 'delete', 'export'],
        'description': 'Hostel management',
    },
    'academic': {
        'actions': ['create', 'read', 'update', 'delete', 'export'],
        'description': 'Academic program management',
    },
    'accounting': {
        'actions': ['create', 'read', 'update', 'delete', 'export', 'generate_report'],
        'description': 'Accounting and finance management',
    },
    'communication': {
        'actions': ['create', 'read', 'update', 'delete', 'send'],
        'description': 'Communication and messaging',
    },
    'teachers': {
        'actions': ['create', 'read', 'update', 'delete', 'export'],
        'description': 'Teacher records management',
    },
    'online_exam': {
        'actions': ['create', 'read', 'update', 'delete', 'publish', 'evaluate'],
        'description': 'Online examination system',
    },
    'reports': {
        'actions': ['read', 'generate', 'export'],
        'description': 'Report generation',
    },
    'store': {
        'actions': ['create', 'read', 'update', 'delete', 'issue', 'return', 'export'],
        'description': 'Store and inventory management',
    },
    'colleges': {
        'actions': ['create', 'read', 'update', 'delete'],
        'description': 'College management',
    },
    'academic_years': {
        'actions': ['create', 'read', 'update', 'delete'],
        'description': 'Academic year management',
    },
    'holidays': {
        'actions': ['create', 'read', 'update', 'delete'],
        'description': 'Holiday management',
    },
    'system_settings': {
        'actions': ['read', 'update'],
        'description': 'System settings management',
    },
}

AVAILABLE_SCOPES = ['none', 'mine', 'team', 'department', 'all']


def get_default_permissions(role):
    """
    Returns default permission JSON for a given role.
    """
    defaults = {
        'admin': {
            # Admin has full access to everything
            resource: {
                action: {'scope': 'all', 'enabled': True}
                for action in config['actions']
            }
            for resource, config in PERMISSION_REGISTRY.items()
        },
        'college_admin': {
            # College admin has full access within their college
            resource: {
                action: {'scope': 'all', 'enabled': True}
                for action in config['actions']
            }
            for resource, config in PERMISSION_REGISTRY.items()
        },
        'teacher': {
            'attendance': {
                'create': {'scope': 'team', 'enabled': True},
                'read': {'scope': 'team', 'enabled': True},
                'update': {'scope': 'team', 'enabled': True},
                'delete': {'scope': 'none', 'enabled': False},
                'export': {'scope': 'team', 'enabled': True},
            },
            'students': {
                'read': {'scope': 'team', 'enabled': True},
                'update': {'scope': 'none', 'enabled': False},
                'create': {'scope': 'none', 'enabled': False},
                'delete': {'scope': 'none', 'enabled': False},
                'import': {'scope': 'none', 'enabled': False},
                'export': {'scope': 'team', 'enabled': True},
            },
            'examinations': {
                'create': {'scope': 'team', 'enabled': True},
                'read': {'scope': 'team', 'enabled': True},
                'update': {'scope': 'team', 'enabled': True},
                'delete': {'scope': 'none', 'enabled': False},
                'publish_results': {'scope': 'team', 'enabled': True},
                'export': {'scope': 'team', 'enabled': True},
            },
            'library': {
                'read': {'scope': 'all', 'enabled': True},
                'create': {'scope': 'none', 'enabled': False},
                'update': {'scope': 'none', 'enabled': False},
                'delete': {'scope': 'none', 'enabled': False},
                'issue_book': {'scope': 'none', 'enabled': False},
                'return_book': {'scope': 'none', 'enabled': False},
                'export': {'scope': 'none', 'enabled': False},
            },
            'online_exam': {
                'create': {'scope': 'team', 'enabled': True},
                'read': {'scope': 'team', 'enabled': True},
                'update': {'scope': 'team', 'enabled': True},
                'delete': {'scope': 'team', 'enabled': True},
                'publish': {'scope': 'team', 'enabled': True},
                'evaluate': {'scope': 'team', 'enabled': True},
            },
            'reports': {
                'read': {'scope': 'team', 'enabled': True},
                'generate': {'scope': 'team', 'enabled': True},
                'export': {'scope': 'team', 'enabled': True},
            },
            'store': {
                'create': {'scope': 'none', 'enabled': False},
                'read': {'scope': 'all', 'enabled': True},
                'update': {'scope': 'none', 'enabled': False},
                'delete': {'scope': 'none', 'enabled': False},
                'issue': {'scope': 'none', 'enabled': False},
                'return': {'scope': 'team', 'enabled': True},
                'export': {'scope': 'none', 'enabled': False},
            },
            'communication': {
                'create': {'scope': 'mine', 'enabled': True},
                'read': {'scope': 'mine', 'enabled': True},
                'update': {'scope': 'mine', 'enabled': True},
                'delete': {'scope': 'mine', 'enabled': True},
                'send': {'scope': 'all', 'enabled': True},
            },
        },
        'student': {
            'attendance': {
                'read': {'scope': 'mine', 'enabled': True},
                'create': {'scope': 'none', 'enabled': False},
                'update': {'scope': 'none', 'enabled': False},
                'delete': {'scope': 'none', 'enabled': False},
                'export': {'scope': 'mine', 'enabled': True},
            },
            'fees': {
                'read': {'scope': 'mine', 'enabled': True},
                'create': {'scope': 'none', 'enabled': False},
                'update': {'scope': 'none', 'enabled': False},
                'delete': {'scope': 'none', 'enabled': False},
                'generate_invoice': {'scope': 'none', 'enabled': False},
                'export': {'scope': 'mine', 'enabled': True},
            },
            'examinations': {
                'read': {'scope': 'mine', 'enabled': True},
                'create': {'scope': 'none', 'enabled': False},
                'update': {'scope': 'none', 'enabled': False},
                'delete': {'scope': 'none', 'enabled': False},
                'publish_results': {'scope': 'none', 'enabled': False},
                'export': {'scope': 'mine', 'enabled': True},
            },
            'library': {
                'read': {'scope': 'mine', 'enabled': True},
                'create': {'scope': 'none', 'enabled': False},
                'update': {'scope': 'none', 'enabled': False},
                'delete': {'scope': 'none', 'enabled': False},
                'issue_book': {'scope': 'none', 'enabled': False},
                'return_book': {'scope': 'none', 'enabled': False},
                'export': {'scope': 'mine', 'enabled': True},
            },
            'online_exam': {
                'read': {'scope': 'mine', 'enabled': True},
                'create': {'scope': 'none', 'enabled': False},
                'update': {'scope': 'none', 'enabled': False},
                'delete': {'scope': 'none', 'enabled': False},
                'publish': {'scope': 'none', 'enabled': False},
                'evaluate': {'scope': 'none', 'enabled': False},
            },
            'communication': {
                'create': {'scope': 'none', 'enabled': False},
                'read': {'scope': 'all', 'enabled': True},
                'update': {'scope': 'none', 'enabled': False},
                'delete': {'scope': 'none', 'enabled': False},
                'send': {'scope': 'none', 'enabled': False},
            },
        },
        'hod': {
            # HOD has department-level access
            resource: {
                action: {'scope': 'department', 'enabled': True}
                for action in config['actions']
            }
            for resource, config in PERMISSION_REGISTRY.items()
        },
        'staff': {
            # Support staff has limited access
            'students': {
                'read': {'scope': 'all', 'enabled': True},
                'create': {'scope': 'all', 'enabled': True},
                'update': {'scope': 'all', 'enabled': True},
                'delete': {'scope': 'none', 'enabled': False},
                'import': {'scope': 'all', 'enabled': True},
                'export': {'scope': 'all', 'enabled': True},
            },
            'library': {
                'create': {'scope': 'all', 'enabled': True},
                'read': {'scope': 'all', 'enabled': True},
                'update': {'scope': 'all', 'enabled': True},
                'delete': {'scope': 'all', 'enabled': True},
                'issue_book': {'scope': 'all', 'enabled': True},
                'return_book': {'scope': 'all', 'enabled': True},
                'export': {'scope': 'all', 'enabled': True},
            },
            'hostel': {
                'create': {'scope': 'all', 'enabled': True},
                'read': {'scope': 'all', 'enabled': True},
                'update': {'scope': 'all', 'enabled': True},
                'delete': {'scope': 'all', 'enabled': True},
                'export': {'scope': 'all', 'enabled': True},
            },
            'store': {
                'create': {'scope': 'all', 'enabled': True},
                'read': {'scope': 'all', 'enabled': True},
                'update': {'scope': 'all', 'enabled': True},
                'delete': {'scope': 'all', 'enabled': True},
                'issue': {'scope': 'all', 'enabled': True},
                'return': {'scope': 'all', 'enabled': True},
                'export': {'scope': 'all', 'enabled': True},
            },
            'communication': {
                'create': {'scope': 'mine', 'enabled': True},
                'read': {'scope': 'mine', 'enabled': True},
                'update': {'scope': 'mine', 'enabled': True},
                'delete': {'scope': 'mine', 'enabled': True},
                'send': {'scope': 'all', 'enabled': True},
            },
        },
        'store_manager': {
            # Store manager has full access to store and inventory operations
            'store': {
                'create': {'scope': 'all', 'enabled': True},
                'read': {'scope': 'all', 'enabled': True},
                'update': {'scope': 'all', 'enabled': True},
                'delete': {'scope': 'all', 'enabled': True},
                'issue': {'scope': 'all', 'enabled': True},
                'return': {'scope': 'all', 'enabled': True},
                'export': {'scope': 'all', 'enabled': True},
            },
            'reports': {
                'read': {'scope': 'all', 'enabled': True},
                'generate': {'scope': 'all', 'enabled': True},
                'export': {'scope': 'all', 'enabled': True},
            },
            'communication': {
                'create': {'scope': 'mine', 'enabled': True},
                'read': {'scope': 'mine', 'enabled': True},
                'update': {'scope': 'mine', 'enabled': True},
                'delete': {'scope': 'mine', 'enabled': True},
                'send': {'scope': 'all', 'enabled': True},
            },
        },
    }
    return defaults.get(role, {})
