from django.db import models


class Database(models.Model):
    name = models.CharField(max_length=255)
    target_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Target(models.Model):
    name = models.CharField(max_length=200)
    database = models.ForeignKey(Database, on_delete=models.CASCADE, related_name='database')
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class File(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    database = models.ForeignKey(Database, on_delete=models.CASCADE)
    file = models.FileField()

    def __str__(self):
        return self.name