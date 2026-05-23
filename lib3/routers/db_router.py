"""
BranchRouter — направляет запросы lending-моделей в БД нужного филиала.
Модели catalog (глобальный каталог) и auth всегда идут в default.
"""

class BranchRouter:
    """
    Модели приложения `lending` читаются/пишутся в БД конкретного филиала.
    Всё остальное (catalog, auth, sessions) — в default.
    """
    BRANCH_APPS = {'lending'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.BRANCH_APPS:
            return hints.get('branch_db', 'branch_1')
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.BRANCH_APPS:
            return hints.get('branch_db', 'branch_1')
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # Разрешаем связи внутри одного приложения
        if obj1._meta.app_label == obj2._meta.app_label:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.BRANCH_APPS:
            # Миграции lending — только в branch_* БД
            return db.startswith('branch_')
        # Остальные (catalog, auth и т.д.) — только в default
        return db == 'default'
