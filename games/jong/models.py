from django.db import models

from django.contrib.auth.models import User

class GameJongResult(models.Model):
    date = models.DateTimeField(auto_now_add=True, blank=True)
    rulejson = models.TextField(blank=True)
    player1 = models.ForeignKey(User,on_delete=models.SET_NULL,blank = True,null=True,related_name="player1")
    player2 = models.ForeignKey(User,on_delete=models.SET_NULL,blank = True,null=True,related_name="player2")
    player3 = models.ForeignKey(User,on_delete=models.SET_NULL,blank = True,null=True,related_name="player3")
    player4 = models.ForeignKey(User,on_delete=models.SET_NULL,blank = True,null=True,related_name="player4")
    score1 = models.IntegerField(blank = True,null=True)
    score2 = models.IntegerField(blank = True,null=True)
    score3 = models.IntegerField(blank = True,null=True)
    score4 = models.IntegerField(blank = True,null=True)
    class Meta:
        app_label = 'matchbox'
    
