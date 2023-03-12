import os.path
import shutil

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from api.models import Database, Target, File
from api.serializers import DatabaseSerializer


class CustomFileSystemStorage(FileSystemStorage):
    def __init__(self, database=None, target=None):
        if database is not None:
            database = settings.MEDIA_ROOT + '/' + database + '/' + target
        super().__init__(database, target)


class FileUploadView(APIView):
    parser_classes = (MultiPartParser,)

    @staticmethod
    def post(request):
        if request.method == 'POST':
            print(request.data)
            file_type = request.data['type']
            db_name = request.data['database']
            target_name = request.data['target']
            print(file_type, db_name, target_name)
            file_obj = request.FILES['file']

            if db_name and target_name:
                if Database.objects.filter(name=db_name).exists():
                    if Target.objects.filter(name=target_name, database=Database.objects.get(name=db_name)).exists():
                        if not File.objects.filter(database=Database.objects.get(name=db_name),
                                                   target=Target.objects.get(name=target_name,
                                                                             database=Database.objects.get(
                                                                                 name=db_name)),
                                                   type=file_type).exists():
                            fs = CustomFileSystemStorage(db_name, target_name)
                            filename = fs.save(file_obj.name, file_obj)
                            file_url = db_name + '/' + fs.url(filename)
                            File.objects.create(name=filename, type=file_type,
                                                target=Target.objects.get(database=Database.objects.get(name=db_name),
                                                                          name=target_name),
                                                database=Database.objects.get(name=db_name), file=file_url)
                            return Response({'message': 'File Uploaded'}, status=status.HTTP_201_CREATED)
                        return Response({'message': file_type + ' File Already Exists'},
                                        status=status.HTTP_409_CONFLICT)
                    return Response({'error': 'Target does not exist'}, status=status.HTTP_404_NOT_FOUND)
                return Response({'error': 'Database does not exist'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'error': 'Please provide all fields'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response({'error': 'BAD REQUEST'}, status=status.HTTP_400_BAD_REQUEST)


class AddDatabase(APIView):
    @staticmethod
    def post(request):
        serializer = DatabaseSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.data['name']
            checkDB = Database.objects.filter(name=name).exists()
            if not checkDB:
                Database.objects.create(name=name)
                return Response(
                    {'message': 'Database  Created', 'details': Database.objects.filter(name=name).values()},
                    status=status.HTTP_201_CREATED)
            return Response({'error': 'Database Already Exists'}, status=status.HTTP_409_CONFLICT)
        return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddTarget(APIView):
    @staticmethod
    def post(request):
        if request.method == 'POST':
            id = request.data['database']
            checkDB = Database.objects.filter(id=id).exists()
            if checkDB:
                target_name = request.data['name']
                checkTarget = Target.objects.filter(name=target_name,
                                                    database=Database.objects.get(id=id)).exists()
                if not checkTarget:
                    Target.objects.create(name=target_name, database=Database.objects.get(id=id))
                    db = Database.objects.get(id=id)
                    db.target_count = Target.objects.filter(database=Database.objects.get(id=id)).count()
                    db.save()
                    return Response(
                        {'message': 'Target Created', 'details': Target.objects.filter(name=target_name).values()},
                        status=status.HTTP_201_CREATED)
                return Response({'error': 'Target already exists'}, status=status.HTTP_409_CONFLICT)
            return Response({'error': 'Database does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return Response('bad request', status=status.HTTP_400_BAD_REQUEST)


class RemoveDatabase(APIView):
    @staticmethod
    def post(request):
        if request.method == 'POST':
            db_name = request.data['name']
            checkDB = Database.objects.filter(name=db_name).exists()
            if checkDB:
                Database.objects.filter(name=db_name).delete()
                path = settings.MEDIA_ROOT + '/' + request.data['name']
                if os.path.exists(path):
                    shutil.rmtree(path)
                return Response({'message': 'Database Deleted'}, status=status.HTTP_200_OK)
            return Response({'error': 'Database does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)


class RemoveTarget(APIView):
    @staticmethod
    def post(request):
        if request.method == 'POST':
            db_name = request.data['database']
            checkDB = Database.objects.filter(name=db_name).exists()
            if checkDB:
                target_name = request.data['name']
                checkTarget = Target.objects.filter(database=Database.objects.get(name=db_name),
                                                    name=target_name).exists()
                if checkTarget:
                    Target.objects.filter(name=target_name).delete()
                    db = Database.objects.get(name=db_name)
                    db.target_count = Target.objects.filter(database=Database.objects.get(name=db_name)).count()
                    db.save()
                    path = settings.MEDIA_ROOT + '/' + request.data['database'] + '/' + request.data['name']
                    if os.path.exists(path):
                        shutil.rmtree(path)
                    return Response({'message': 'Target Deleted'}, status=status.HTTP_200_OK)
                return Response({'error': 'Target does not exist'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'error': 'Database does not exist'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'bad request'}, status=status.HTTP_400_BAD_REQUEST)


class GetAllDatabases(APIView):
    @staticmethod
    def get(request):
        if request.method == 'GET':
            return Response({'message': Database.objects.values()}, status=status.HTTP_200_OK)
        return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)


class GetAllTargets(APIView):
    @staticmethod
    def get(request):
        if request.method == 'GET':
            targets = Target.objects.values()
            if len(targets):
                return Response({'message': targets}, status=status.HTTP_200_OK)
            return Response({'error': 'No targets Available'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)


class GetAllTargetsByDatabase(APIView):
    @staticmethod
    def get(request):
        if request.method == 'GET':
            params = request.query_params.get('database', None)
            if params is not None:
                checkDB = Database.objects.filter(id=params).exists()
                if checkDB:
                    targets = Target.objects.filter(database=params).values()
                    if len(targets):
                        return Response({'message': targets}, status=status.HTTP_200_OK)
                    return Response({'error': 'No targets Available'}, status=status.HTTP_404_NOT_FOUND)
                return Response({'error': 'Database does not exist'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'error': 'Empty or Bad Parameter Request'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)


class GetAllFiles(APIView):
    @staticmethod
    def get(request):
        if request.method == 'GET':
            files = File.objects.values('file')
            if len(files):
                return Response({'message': files}, status=status.HTTP_200_OK)
            return Response({'error': 'No Files Available'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)


class GetDatabaseById(APIView):
    @staticmethod
    def get(request):
        if request.method == 'GET':
            params = request.query_params.get('db', None)
            if params is not None:
                checkDB = Database.objects.filter(id=params).exists()
                if checkDB:
                    return Response({'message': Database.objects.filter(id=params).values()}, status=status.HTTP_200_OK)
                return Response({'error': 'Database does not exist'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'error': 'Empty or Bad Parameter Request'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)


class GetFilesByTargetId(APIView):
    @staticmethod
    def get(request):
        if request.method == 'GET':
            params = request.query_params.get('target', None)
            if params is not None:
                checkTarget = Target.objects.filter(id=params).exists()
                if checkTarget:
                    return Response({'message': File.objects.filter(target=Target.objects.get(id=params)).values()}, status=status.HTTP_200_OK)
                return Response({'error': 'Target does not exist'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'error': 'Empty or Bad Parameter Request'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)
