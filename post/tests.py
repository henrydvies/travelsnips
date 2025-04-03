from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from post.models import Post, SubPost, PostAssociation, PostImage
import json

User = get_user_model()

class PostViewsTest(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpassword1'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpassword2'
        )
        
        # Create a test post
        self.post = Post.objects.create(
            title='Test Post',
            description='This is a test post description',
            owner=self.user1,
            location_name='Test Location',
            latitude=51.5074,
            longitude=-0.1278
        )
        
        # Add user1 as associated person to the post
        self.post.add_associated_person(self.user1)
        
        # Create a test subpost
        self.subpost = SubPost.objects.create(
            post=self.post,
            subpost_title='Test SubPost',
            content='This is a test subpost content',
            order=0
        )
        
        # Setup client
        self.client = Client()
        
        # Create a simple test image for uploads
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b',
            content_type='image/jpeg'
        )
    
    def test_post_detail_view_owner(self):
        """Test that the post owner can view the post detail page"""
        # Login as post owner
        self.client.login(username='testuser1', password='testpassword1')
        
        # Get the post detail page
        response = self.client.get(reverse('post_detail', args=[self.post.id]))
        
        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)
        
        # Check that the post data is in the context
        self.assertEqual(response.context['post'], self.post)
        self.assertTrue(response.context['is_owner'])
        self.assertTrue(response.context['is_associated'])
    
    def test_post_detail_view_unauthorized(self):
        """Test that unauthorized users cannot view the post detail page"""
        # Login as user2 (not the post owner or associated)
        self.client.login(username='testuser2', password='testpassword2')
        
        # Mock the get_all_linked_users method to return an empty list
        # This is needed because in your actual code, this method is used
        # to check if the user is linked to the post owner
        def mock_get_linked_users():
            return []
        
        original_method = self.user1.get_all_linked_users
        self.user1.get_all_linked_users = mock_get_linked_users
        
        try:
            # Get the post detail page
            response = self.client.get(reverse('post_detail', args=[self.post.id]))
            
            # Check that the response is 403 Forbidden
            self.assertEqual(response.status_code, 403)
        finally:
            # Restore the original method
            self.user1.get_all_linked_users = original_method
    
    def test_create_post_view(self):
        """Test creating a new post"""
        # Login
        self.client.login(username='testuser1', password='testpassword1')
        
        # Mock the get_all_linked_users method to return a list with user1
        def mock_get_linked_users():
            return [self.user1]
        
        original_method = self.user1.get_all_linked_users
        self.user1.get_all_linked_users = mock_get_linked_users
        
        try:
            # Post data to create a new post
            post_data = {
                'title': 'New Test Post',
                'description': 'This is a new test post',
                'latitude': '52.5200',
                'longitude': '13.4050',
                'location_name': 'Berlin, Germany',
                'post_icon': self.test_image
            }
            
            # Send POST request
            response = self.client.post(reverse('create_post'), post_data)
            
            # Check that the response is a redirect (302)
            self.assertEqual(response.status_code, 302)
            
            # Get the newly created post
            new_post = Post.objects.get(title='New Test Post')
            
            # Check that the post data is correct
            self.assertEqual(new_post.title, 'New Test Post')
            self.assertEqual(new_post.description, 'This is a new test post')
            self.assertEqual(new_post.latitude, 52.52)
            self.assertEqual(new_post.longitude, 13.405)
            self.assertEqual(new_post.location_name, 'Berlin, Germany')
            self.assertEqual(new_post.owner, self.user1)
            
            # Check that the current user is associated with the post
            self.assertTrue(self.user1 in new_post.get_associated_people())
        finally:
            # Restore the original method
            self.user1.get_all_linked_users = original_method
    
    def test_create_post_view_no_title(self):
        """Test that a post cannot be created without a title"""
        # Login
        self.client.login(username='testuser1', password='testpassword1')
        
        # Post data without a title
        post_data = {
            'description': 'This post has no title',
            'latitude': '52.5200',
            'longitude': '13.4050',
            'location_name': 'Berlin, Germany'
        }
        
        # Send POST request
        response = self.client.post(reverse('create_post'), post_data)
        
        # Check that the response is a 400 Bad Request
        self.assertEqual(response.status_code, 400)
        
        # Check that the response contains the error message
        self.assertContains(response, 'Title is required', status_code=400)
    
    def test_manage_associations_view(self):
        """Test managing post associations"""
        # Login as post owner
        self.client.login(username='testuser1', password='testpassword1')
        
        # Add user2 as an associated person
        post_data = {
            'action': 'add',
            'user_id': str(self.user2.id)
        }
        
        response = self.client.post(
            reverse('manage_associations', args=[self.post.id]),
            post_data
        )
        
        # Check that the response is 200 OK and is JSON
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check that the operation was successful
        self.assertTrue(data['success'])
        
        # Check that user2 is now associated with the post
        self.assertTrue(self.user2 in self.post.get_associated_people())
        
        # Now remove user2
        post_data = {
            'action': 'remove',
            'user_id': str(self.user2.id)
        }
        
        response = self.client.post(
            reverse('manage_associations', args=[self.post.id]),
            post_data
        )
        
        # Check that the response is 200 OK and is JSON
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check that the operation was successful
        self.assertTrue(data['success'])
        
        # Check that user2 is no longer associated with the post
        self.assertFalse(self.user2 in self.post.get_associated_people())
    
    def test_edit_post_view(self):
        """Test editing a post"""
        # Login as post owner
        self.client.login(username='testuser1', password='testpassword1')
        
        # Edit the post
        post_data = {
            'title': 'Updated Test Post',
            'description': 'This is an updated test post description'
        }
        
        response = self.client.post(
            reverse('edit_post', args=[self.post.id]),
            post_data
        )
        
        # Check that the response is 200 OK and is JSON
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check that the operation was successful
        self.assertTrue(data['success'])
        
        # Refresh the post from the database
        self.post.refresh_from_db()
        
        # Check that the post data has been updated
        self.assertEqual(self.post.title, 'Updated Test Post')
        self.assertEqual(self.post.description, 'This is an updated test post description')
    
    def test_add_subpost_view(self):
        """Test adding a new subpost"""
        # Login as associated user
        self.client.login(username='testuser1', password='testpassword1')
        
        # Create a new subpost
        post_data = {
            'title': 'New SubPost',
            'content': 'This is a new subpost content'
        }
        
        # Add a test image
        post_data['images'] = self.test_image
        
        response = self.client.post(
            reverse('add_subpost', args=[self.post.id]),
            post_data
        )
        
        # Check that the response is 200 OK and is JSON
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check that the operation was successful
        self.assertTrue(data['success'])
        
        # Check that the subpost was created
        subpost = SubPost.objects.get(subpost_title='New SubPost')
        self.assertEqual(subpost.content, 'This is a new subpost content')
        self.assertEqual(subpost.post, self.post)
    
    def test_edit_subpost_view(self):
        """Test editing a subpost"""
        # Login as associated user
        self.client.login(username='testuser1', password='testpassword1')
        
        # Edit the subpost
        post_data = {
            'title': 'Updated SubPost',
            'content': 'This is an updated subpost content'
        }
        
        response = self.client.post(
            reverse('edit_subpost', args=[self.subpost.id]),
            post_data
        )
        
        # Check that the response is 200 OK and is JSON
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Parse the JSON response
        data = json.loads(response.content)
        
        # Check that the operation was successful
        self.assertTrue(data['success'])
        
        # Refresh the subpost from the database
        self.subpost.refresh_from_db()
        
        # Check that the subpost data has been updated
        self.assertEqual(self.subpost.subpost_title, 'Updated SubPost')
        self.assertEqual(self.subpost.content, 'This is an updated subpost content')
    
    def test_post_locations_api(self):
        """Test the post locations API endpoint"""
        # Login
        self.client.login(username='testuser1', password='testpassword1')
        
        # Mock the get_all_visible_posts method to return a list with the test post
        def mock_get_visible_posts():
            return [self.post]
        
        original_method = self.user1.get_all_visible_posts
        self.user1.get_all_visible_posts = mock_get_visible_posts
        
        try:
            # Get the post locations
            response = self.client.get(reverse('post_locations'))
            
            # Check that the response is 200 OK and is JSON
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/json')
            
            # Parse the JSON response
            data = json.loads(response.content)
            
            # Check that the response contains the post
            self.assertEqual(len(data['posts']), 1)
            self.assertEqual(data['posts'][0]['id'], self.post.id)
            self.assertEqual(data['posts'][0]['title'], 'Test Post')
            self.assertEqual(data['posts'][0]['latitude'], 51.5074)
            self.assertEqual(data['posts'][0]['longitude'], -0.1278)
            self.assertEqual(data['posts'][0]['location_name'], 'Test Location')
        finally:
            # Restore the original method
            self.user1.get_all_visible_posts = original_method