class MyAppRouter:
    """
    A router to control all database operations on models for the
    'app1' and 'app2' applications.
    """

    def db_for_read(self, model, **hints):
        """Attempts to read app models go to 'default' db."""
        if model._meta.app_label == 'conteneurs':
            return 'default'
        elif model._meta.app_label == 'stock_backend':
            return 'autre_base'
        return None

    def db_for_write(self, model, **hints):
        """Attempts to write app models go to 'default' db."""
        if model._meta.app_label == 'conteneurs':
            return 'default'
        elif model._meta.app_label == 'stock_backend':
            return 'autre_base'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if a model in the conteneurs or app2 is involved."""
        if obj1._meta.app_label == 'conteneurs' or obj2._meta.app_label == 'conteneurs':
            return True
        elif obj1._meta.app_label == 'stock_backend' or obj2._meta.app_label == 'stock_backend':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that the app's models get created on the right database."""
        if app_label == 'conteneurs':
            return db == 'default'
        elif app_label == 'stock_backend':
            return db == 'autre_base'
        return None
