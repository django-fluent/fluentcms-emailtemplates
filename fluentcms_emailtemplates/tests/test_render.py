from django.test import TestCase
from fluent_contents.models import Placeholder
from fluentcms_emailtemplates.models import EmailTemplate
from fluentcms_emailtemplates.plugins.emailtext.models import EmailTextItem

class RenderingTests(TestCase):
    """
    Test the rendering of the email template
    """

    def test_text_render(self):
        emailtemplate = EmailTemplate.objects.language('en').create(name='foo', slug='foo')
        emailtemplate.create_translation('en', subject='Hi {first_name}!')

        p = Placeholder.objects.create_for_object(emailtemplate, slot='email_templates')
        EmailTextItem.objects.create_for_placeholder(
            placeholder=p,
            html="<p>Hello {first_name}!</p><p>How are you?</p>"
        )

        content = emailtemplate.get_content(base_url='http://testserver/', context={'first_name': "John"})
        expected_html = '<html><head><title>Hi John!</title></head>\n<body><div><p>Hello John!</p><p>How are you?</p></div>\n\n</body></html>'
        expected_text = 'Hello John!\n\nHow are you?\n'

        self.assertEqual(content.subject, "Hi John!")
        self.assertEqual(content.html, expected_html)
        self.assertEqual(content.text, expected_text)
