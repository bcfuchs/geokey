# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HistoricalObservation'
        db.create_table(u'contributions_historicalobservation', (
            (u'id', self.gf('django.db.models.fields.IntegerField')(db_index=True, blank=True)),
            ('location_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('project_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('category_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='active', max_length=20)),
            ('review_comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('attributes', self.gf(u'django_hstore.fields.DictionaryField')(db_index=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
            ('creator_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updator_id', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('search_matches', self.gf('django.db.models.fields.TextField')()),
            (u'history_id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            (u'history_date', self.gf('django.db.models.fields.DateTimeField')()),
            (u'history_user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.User'], null=True)),
            (u'history_type', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal(u'contributions', ['HistoricalObservation'])

        # Adding model 'Observation'
        db.create_table(u'contributions_observation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(related_name='locations', to=orm['contributions.Location'])),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(related_name='observations', to=orm['projects.Project'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['categories.Category'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='active', max_length=20)),
            ('review_comment', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('attributes', self.gf(u'django_hstore.fields.DictionaryField')(db_index=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='creator', to=orm['users.User'])),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('updator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='updator', null=True, to=orm['users.User'])),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('search_matches', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('contributions', ['Observation'])

        # Adding model 'Comment'
        db.create_table(u'contributions_comment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.User'])),
            ('commentto', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comments', to=orm['contributions.Observation'])),
            ('respondsto', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='responses', null=True, to=orm['contributions.Comment'])),
            ('status', self.gf('django.db.models.fields.CharField')(default='active', max_length=20)),
        ))
        db.send_create_signal('contributions', ['Comment'])

        # Adding model 'Location'
        db.create_table(u'contributions_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('geometry', self.gf('django.contrib.gis.db.models.fields.GeometryField')(geography=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.User'])),
            ('version', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('private', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('private_for_project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'], null=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='active', max_length=20)),
        ))
        db.send_create_signal('contributions', ['Location'])

        # Adding model 'MediaFile'
        db.create_table(u'contributions_mediafile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('contribution', self.gf('django.db.models.fields.related.ForeignKey')(related_name='files_attached', to=orm['contributions.Observation'])),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['users.User'])),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='active', max_length=20)),
        ))
        db.send_create_signal('contributions', ['MediaFile'])

        # Adding model 'ImageFile'
        db.create_table(u'contributions_imagefile', (
            (u'mediafile_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['contributions.MediaFile'], unique=True, primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal('contributions', ['ImageFile'])

        # Adding model 'VideoFile'
        db.create_table(u'contributions_videofile', (
            (u'mediafile_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['contributions.MediaFile'], unique=True, primary_key=True)),
            ('video', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('youtube_id', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('thumbnail', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True)),
            ('youtube_link', self.gf('django.db.models.fields.URLField')(max_length=255, null=True, blank=True)),
            ('swf_link', self.gf('django.db.models.fields.URLField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('contributions', ['VideoFile'])


    def backwards(self, orm):
        # Deleting model 'HistoricalObservation'
        db.delete_table(u'contributions_historicalobservation')

        # Deleting model 'Observation'
        db.delete_table(u'contributions_observation')

        # Deleting model 'Comment'
        db.delete_table(u'contributions_comment')

        # Deleting model 'Location'
        db.delete_table(u'contributions_location')

        # Deleting model 'MediaFile'
        db.delete_table(u'contributions_mediafile')

        # Deleting model 'ImageFile'
        db.delete_table(u'contributions_imagefile')

        # Deleting model 'VideoFile'
        db.delete_table(u'contributions_videofile')


    models = {
        u'categories.category': {
            'Meta': {'object_name': 'Category'},
            'colour': ('django.db.models.fields.TextField', [], {'default': "'#0033ff'"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"}),
            'default_status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '20'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'categories'", 'to': u"orm['projects.Project']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            'symbol': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'})
        },
        'contributions.comment': {
            'Meta': {'ordering': "['id']", 'object_name': 'Comment'},
            'commentto': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': "orm['contributions.Observation']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'respondsto': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'responses'", 'null': 'True', 'to': "orm['contributions.Comment']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'contributions.historicalobservation': {
            'Meta': {'ordering': "(u'-history_date', u'-history_id')", 'object_name': 'HistoricalObservation'},
            'attributes': (u'django_hstore.fields.DictionaryField', [], {'db_index': 'True'}),
            'category_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'creator_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            u'history_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'history_id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            u'history_type': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'history_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']", 'null': 'True'}),
            u'id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'blank': 'True'}),
            'location_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'project_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'review_comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'search_matches': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'updator_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'contributions.imagefile': {
            'Meta': {'ordering': "['id']", 'object_name': 'ImageFile', '_ormbases': ['contributions.MediaFile']},
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'mediafile_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['contributions.MediaFile']", 'unique': 'True', 'primary_key': 'True'})
        },
        'contributions.location': {
            'Meta': {'object_name': 'Location'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'geometry': ('django.contrib.gis.db.models.fields.GeometryField', [], {'geography': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'private_for_project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['projects.Project']", 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'contributions.mediafile': {
            'Meta': {'ordering': "['id']", 'object_name': 'MediaFile'},
            'contribution': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'files_attached'", 'to': "orm['contributions.Observation']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'})
        },
        'contributions.observation': {
            'Meta': {'ordering': "['updated_at', 'id']", 'object_name': 'Observation'},
            'attributes': (u'django_hstore.fields.DictionaryField', [], {'db_index': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['categories.Category']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'creator'", 'to': u"orm['users.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'locations'", 'to': "orm['contributions.Location']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'observations'", 'to': u"orm['projects.Project']"}),
            'review_comment': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'search_matches': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'updator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'updator'", 'null': 'True', 'to': u"orm['users.User']"}),
            'version': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        'contributions.videofile': {
            'Meta': {'ordering': "['id']", 'object_name': 'VideoFile', '_ormbases': ['contributions.MediaFile']},
            u'mediafile_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['contributions.MediaFile']", 'unique': 'True', 'primary_key': 'True'}),
            'swf_link': ('django.db.models.fields.URLField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True'}),
            'video': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'youtube_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'youtube_link': ('django.db.models.fields.URLField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'projects.admins': {
            'Meta': {'ordering': "['project__name']", 'unique_together': "(('project', 'user'),)", 'object_name': 'Admins'},
            'contact': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'admin_of'", 'to': u"orm['projects.Project']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'has_admins'", 'to': u"orm['users.User']"})
        },
        u'projects.project': {
            'Meta': {'ordering': "['name']", 'object_name': 'Project'},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'admins'", 'symmetrical': 'False', 'through': u"orm['projects.Admins']", 'to': u"orm['users.User']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['users.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'everyone_contributes': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'geographic_extend': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'geography': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isprivate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '20'})
        },
        u'users.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'display_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['contributions']