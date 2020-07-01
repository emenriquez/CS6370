from django.db import models

# Create your models here.
class Document(models.Model):
    id = models.CharField(primary_key=True, max_length=100, unique=True)
    title = models.CharField(max_length=100)
    snippet = models.CharField(max_length=200)
    vector_length = models.FloatField(default=0)
    max_freq = models.IntegerField(default=0)

    def __str__(self):
        return self.id
    
    @property
    def correlated(self):
        "Returns a custom property of documents"
        correlated_docs = correlatedDocs.objects.filter(doc=self.id)
        correlated_docs = correlated_docs.values_list('corrDoc', flat=True).order_by('-score')
        corrDocObjects = [Document.objects.get(id=result) for result in correlated_docs]

        return corrDocObjects

class Word(models.Model):
    id = models.CharField(primary_key=True, max_length=100, unique=True)
    df = models.IntegerField(default=0)

    def __str__(self):
        return self.id

class Occurrence(models.Model):
    word = models.ForeignKey('Word', on_delete=models.CASCADE)
    doc_id = models.ForeignKey('Document', on_delete=models.CASCADE)
    freq = models.IntegerField(default=0)
    tf_idf = models.FloatField(default=0.0)
    locations = models.CharField(max_length=5000)

    def __str__(self):
        return (f'{self.word}: {self.doc_id}')

class Keyword(models.Model):
    word = models.ForeignKey('Word', on_delete=models.CASCADE, related_name='root_word')
    keyword = models.ForeignKey('Word', related_name='keyword', on_delete=models.CASCADE)
    score = models.FloatField(default=0.0)

    def __str__(self):
        return (f'{self.word} <- {self.keyword}')

class correlatedDocs(models.Model):
    doc = models.ForeignKey('Document', on_delete=models.CASCADE, related_name='doc')
    corrDoc = models.ForeignKey('Document', on_delete=models.CASCADE, related_name='corrDoc')
    score = models.FloatField(default=0.0)