from django.urls import path

from .views import FileUploadView, AddDatabase, AddTarget, RemoveTarget, RemoveDatabase, GetAllDatabases, GetAllTargets, \
    GetAllTargetsByDatabase, GetAllFiles, GetAllFilesByTarget, GetDatabaseById

urlpatterns = [
    path('addDatabase', AddDatabase.as_view()),
    path('removeDatabase', RemoveDatabase.as_view()),
    path('getAllDatabases', GetAllDatabases.as_view()),
    path('getAllTargetsByDatabase', GetAllTargetsByDatabase.as_view()),
    path('getDatabaseById', GetDatabaseById.as_view()),

    path('addTarget', AddTarget.as_view()),
    path('removeTarget', RemoveTarget.as_view()),
    path('getAllTargets', GetAllTargets.as_view()),

    path('upload', FileUploadView.as_view()),
    path('getAllFiles', GetAllFiles.as_view()),
    path('getAllFilesByTarget', GetAllFilesByTarget.as_view())
]
