from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from catalog.models import Author, BookInstance, Book, Genre


class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_authors = 13
        for i in range(number_of_authors):
            Author.objects.create(first_name='Christian %s' % i, last_name='Surname %s' % i)

    def test_view_url_exist_at_desire_location(self):
        resp = self.client.get('/catalog/authors/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

    def test_uses_correct_template(self):
        resp = self.client.get(reverse('authors'))
        self.assertTemplateUsed(resp, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        resp = self.client.get(reverse('authors'))
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] is True)

    def test_list_all_authors(self):
        resp = self.client.get(reverse('authors'), {'page': 2})
        self.assertEqual(len(resp.context['author_list']), 3)


class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()

        test_author = Author.objects.create(first_name='John', last_name='Smith')
        Genre.objects.create(name='Fantasy')
        test_genre = Genre.objects.all()
        test_book = Book.objects.create(title='Book Title', summary='My book summary', isbn='ABCDEFG', author=test_author)
        test_book.genre.set(test_genre)
        test_book.save()

        number_of_book_copies = 30
        for i in range(number_of_book_copies):
            return_date = timezone.now() + timedelta(days=i % 5)
            if i % 2:
                borrower = test_user1
            else:
                borrower = test_user2
            status = 'm'
            BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2016', due_back=return_date, borrower=borrower, status=status)

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(resp, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))
        self.assertEqual(str(resp.context['user']), 'testuser1')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_book_in_list(self):
        self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))
        self.assertTrue('bookinstance_list' in resp.context)
        self.assertEqual(len(resp.context['bookinstance_list']), 0)

        get_ten_books = BookInstance.objects.all()
        for copy in get_ten_books:
            copy.status = 'o'
            copy.save()

        resp = self.client.get(reverse('my-borrowed'))
        for bookitem in resp.context['bookinstance_list']:
            self.assertEqual(resp.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)

    def test_pages_order_by_due_date(self):
        for copy in BookInstance.objects.all():
            copy.status = 'o'
            copy.save()
        self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))
        self.assertEqual(len(resp.context['bookinstance_list']), 10)
        last_date = date.today() - timedelta(weeks=10)
        for copy in resp.context['bookinstance_list']:
            self.assertTrue(last_date <= copy.due_back)
