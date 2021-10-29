from django.views.generic import View

from django.core.mail import send_mail
from django.conf import settings

import os
import requests
from django.http import JsonResponse

from django.shortcuts import get_object_or_404
from blog.models import CaseStudy, Post

import json

class FailView(View):
    def get(self, request):
        raise Exception("This is a fail test to verify DEBUG mode.")

class HealthCheckView(View):
    def get(self, request):
        return JsonResponse({
            'message': 'django health check ok.'
        }, status=200)

class EmailReportMixin(object):
    HTML_MESSAGE = ''
    visitor_info_dict = {}
    ng_visiting_path = ''
    request = None

    def send_feedback_notice_email(self, request, include_angular_report=False, contact_form_html=None):
        self.HTML_MESSAGE = ''
        self.request = request

        # contact me form submit
        if contact_form_html:
            self.HTML_MESSAGE += contact_form_html
            self.HTML_MESSAGE += """
                <h1 align="center">Visitor Report</h1>
                """

        # collect all reporter params
        self.visitor_info_dict.update({ 'Django': self.prepare_django_report() })
        if include_angular_report:
            self.visitor_info_dict.update({ 'Angular': self.prepare_angular_report() })

        # quick look up geo / visiting path from angular SPA routing
        #
        #
        report_flags = []
        # lookup geo from dj
        try:
            ip_geo_info = self.visitor_info_dict['Django']['IP_address_x_forwarded_for_0']
            report_flags.append(ip_geo_info['city'] + ':Dj')
        except:
            print('\n\n\nfailed to get city from ip\n\n\n', self.visitor_info_dict['Django'])

        if include_angular_report:
            # lookup geo from ng
            try:
                report_flags.append(self.visitor_info_dict['Angular']['city'][0] + ':Ng')
            except:
                pass
            # if accessing specific doc, get that doc title
            try:
                report_flags.append('"{}":Ng'.format(self.visitor_info_dict['Angular']['visited_doc_title']))
            except:
                report_flags.append('{}:Ng'.format(self.ng_visiting_path))


        # push in all the report params
        #
        #
        for reporter, report in self.visitor_info_dict.items():
            if contact_form_html:
                self.HTML_MESSAGE += """
                <h2>{} Reporter Data</h2>
                """.format(reporter)
            self.generate_report_html(report, use_markdown= not contact_form_html)


        # ready to send notification (email or slack)
        #
        #
        SUBJECT = ''
        if len(report_flags) != 0:
            SUBJECT = ' | '.join(report_flags) + '......'

        if contact_form_html:
            SUBJECT = SUBJECT + "New Message from Iriversland2"
        else:
            SUBJECT = SUBJECT + "👋 Visitor Report from Iriversland2"

        MESSAGE = self.HTML_MESSAGE
        if contact_form_html:
            FROM = settings.SERVER_EMAIL
            TO = ['shaungc@umich.edu']
            send_mail(SUBJECT, MESSAGE, FROM, TO, html_message=self.HTML_MESSAGE)
        else:
            requests.post(url=settings.SEND_MESSAGE_URL, json={
                # see structure at https://api.slack.com/block-kit/building
                'channel': 'iriversland-notif',
                'username': 'Iriversland Notification',
                'blocks': [{
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'*{SUBJECT}*'
                    }
                },{
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': MESSAGE
                    }
                }]
            })


    def generate_report_html(self, info_dict, use_markdown=False):
        for key, value in info_dict.items():
            try:
                normalized_str_value = json.dumps(value)
            except:
                normalized_str_value = repr(value)

            if use_markdown:
                self.HTML_MESSAGE += f'*{key}:* `{normalized_str_value}` '
            else:
                self.HTML_MESSAGE += """
                <p><strong>{}</strong>: {}</p>
                """.format(key, normalized_str_value )

    def prepare_angular_report(self):
        ng_visitor_info_dict = {}

        self.ng_visiting_path = self.request.GET.get('visitingPath', '(path empty)')

        if 'portfolio' or 'blog' in self.ng_visiting_path:
            visited_doc_id = self.ng_visiting_path.split('/')[-1]
            visited_doc_route = self.ng_visiting_path.split('/')[-2]
            if visited_doc_id.isdigit():
                try:
                    if visited_doc_route == 'portfolio':
                        doc_obj = CaseStudy.objects.get(id=visited_doc_id)
                    elif visited_doc_route == 'blog':
                        doc_obj = get_object_or_404(Post, pk=visited_doc_id)

                    ng_visitor_info_dict.update({ 'visited_doc_title': doc_obj.title })
                except Exception as e:
                    print('Error while getting doc object for id {}'.format(visited_doc_id), repr(e))
                    ng_visitor_info_dict.update({ "angular cannot get case study title. id is {}".format(visited_doc_id): '' })

        for key, value in dict(self.request.GET._iterlists()).items():
            ng_visitor_info_dict.update({ key: value })

        return ng_visitor_info_dict


    def prepare_django_report(self):
        dj_visitor_info_dict = {}
        # Visitor detail info report
        dj_visitor_info_dict.update(self.getVisitorNotificationData())
        return dj_visitor_info_dict

    def getBasicInfo(self, visitor_info):
        try:
            visitor_info['name'] = str(self.request.user)
        except Exception as e:
            visitor_info['error_getting_basic_info'] = 'error message: {}'.format(e)

    def getMoreInfo(self, visitor_info):
        '''
        django request object see more entries on https://docs.djangoproject.com/en/2.0/ref/request-response/#httprequest-objects
        get real ip address in django see https://stackoverflow.com/questions/4581789/how-do-i-get-user-ip-address-in-django
        look up loaction from ip address see https://www.iplocation.net
        using ip geolocation lookup api see https://ipinfo.io
        '''
        try:
            visitor_info['IP_address_django_get_host'] = self.request.get_host()
            visitor_info['IP_address_django_remote_address'] = self.request.META.get('REMOTE_ADDR', '(empty)')

            x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_list = x_forwarded_for.split(',')
                visitor_info['IP_address_x_forwarded_for'] = str( ip_list )
                i = 0
                for ip in ip_list:
                    if ip == '':
                        continue

                    # ip stack api free plan does not allow https so just use http
                    stack_api = requests.get('http://api.ipstack.com/{}'.format(ip), params={
                        'access_key': os.environ['IPSTACK_API_TOKEN'],
                        'fields': 'city, region_name, country_name, zip, ip, hostname, type, continent_name, latitude, longitude'
                    }).json()

                    # ip info api
                    info_api = requests.get('https://ipinfo.io/{}/json'.format(ip), params={'token': os.environ['IPINFO_API_TOKEN'] }).json()

                    visitor_info['IP_address_x_forwarded_for_{}_stack_api'.format(i)] = stack_api
                    visitor_info['IP_address_x_forwarded_for_{}_info_api'.format(i)] = info_api

                    i += 1

            else:
                visitor_info['IP_address_x_forwarded_for'] = '(empty)'

            visitor_info["user_agent"] = self.request.META.get('HTTP_USER_AGENT', '(empty)')
        except Exception as e:
            visitor_info['error_getting_more_info'] = 'error message: {}'.format(e)

    def getVisitorNotificationData(self):
        visitor_info = {}
        self.getBasicInfo(visitor_info)
        self.getMoreInfo(visitor_info)
        return visitor_info






class EmailView(EmailReportMixin, View):

    def get(self, request, **kwargs):
        print('incoming email GET request...')
        if request.user.is_superuser:
            print('is superuser so bypass')
            return JsonResponse({
                'message': 'BYPASS ADMIN',
            })
        else:
            print('random user, will now process email request')
            query = self.request.GET.get('query', '')
            if query == 'get_api_key':
                print('getting api key')
                return JsonResponse({
                    'message': 'OK',
                    'data': os.environ['IPINFO_API_TOKEN'],
                })
            elif query == 'report_visit':
                print('ready to send report email')
                self.send_feedback_notice_email(request, include_angular_report=True)
                return JsonResponse({
                    'message': 'OK',
                })






class ContactMeView(EmailReportMixin, View):
    def get(self, request, **kwargs):
        user_response = request.GET.get('response', '')
        if user_response == '':
            return JsonResponse({
                'message': 'no recaptcha response given'
            })

        secret = os.environ['RECAPTCHA_SECRET']
        post_url = 'https://www.google.com/recaptcha/api/siteverify'
        post_data = {
            'secret': secret,
            'response': user_response
        }
        verification_result = requests.post(post_url, data=post_data).json()
        print("\n\n\nrecaptcha verification result is:", verification_result, '\n\n\n')

        if verification_result['success'] or verification_result['success'] == 'true':
            email = request.GET.get('email', '')
            name = request.GET.get('name', '')
            message = request.GET.get('message', '')
            html_email_content = '''
                <h1 align="center">Incoming Visitor Message</h1>
                <p align="center">A visitor filled out the contact form and left you a message.</p>
                <strong>Visitor Email:</strong> {}<br>
                <strong>Visitor Name:</strong> {}<br>
                <h2 align="center">Visitor Message</h2>
                <p>{}</p>
            '''.format(email, name, message)
            self.send_feedback_notice_email(request, contact_form_html=html_email_content)

        return JsonResponse(verification_result)