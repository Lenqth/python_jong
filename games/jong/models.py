from django.db import models

from django.contrib.auth.models import User

class GameJongResult(models.Model):
    date = models.DateTimeField(auto_now_add=True, blank=True)
    rulejson = models.JSONField()
    player1 = models.ForeignKey(User,null=True)
    player2 = models.ForeignKey(User,null=True)
    player3 = models.ForeignKey(User,null=True)
    player4 = models.ForeignKey(User,null=True)
    score1 = models.IntegerField()
    score2 = models.IntegerField()
    score3 = models.IntegerField()
    score4 = models.IntegerField()
    
