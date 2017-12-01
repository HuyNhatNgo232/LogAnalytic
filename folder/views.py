# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages

from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from folder.forms import ItemForm, RegistrationForm, DatePickerForm
from folder.models import Folder, Item
from django.views.generic import View
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from operator import itemgetter
from django.contrib.auth.forms import PasswordChangeForm
from datetime import date
import datetime


import os

# Create your views here.
file_up_name = ''
item_pk = ''
check_item_pk = ''
user_id = ''
start = ''
end = ''

class IndexView(ListView):
    template_name = 'folder/index.html'
    context_object_name = 'folder_list'

    def get_queryset(self):
        global user_id
        user_id = str(self.request.user.id)
        global start
        global end
        start = ""
        end = ""
        print user_id
        print "main view"
        return Folder.objects.all()


class FolderDetailView(DetailView):
    model = Folder
    template_name = 'folder/folder_detail.html'
    context_object_name = 'folder'


class MyFolder(IndexView):
    def get_queryset(self):
        print "something"
        return Folder.objects.filter(created_by=self.request.user.id)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        print "dispatch"
        return super(MyFolder, self).dispatch(*args, **kwargs)


class NewFolderView(CreateView):
    model = Folder
    fields = ['title', ]

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super(NewFolderView, self).form_valid(form)


class EditFolderView(UpdateView):
    model = Folder
    fields = ['title', ]

    def get_queryset(self):
        base_qs = super(EditFolderView, self).get_queryset()
        return base_qs.filter(created_by=self.request.user)


class DeleteFolderView(DeleteView):
    model = Folder
    success_url = reverse_lazy('folder_list')


####################### Back-end ################################



def data(current_user_id):

    global file_up_name

    if file_up_name.__contains__(" "):
        file_up_name = file_up_name.replace(" ","_")
    global file_up_name
    logfile = open(file_up_name, 'r')

    # Keys of dictionary are the error names.
    dictionary = dict()
    usage_dictionary = dict()
    line_number = 0

    '''
    # Flag for prompting which errors to look for
    keep_prompting = True

    error_names = []
    error_volume = []
    ax = plt.subplot()
    '''

    def verifyController(line):
        controller_list = ['DockerServerController', 'DockerVolumeController', 'ProvisionController',
                           'BlueprintController']
        controller_found = ""
        for c in controller_list:
            if c in line:
                controller_found = controller_found + c + ", "
        return controller_found[:-2]

    def verifyException(line):
        exception_list = ['AccessDeniedException', 'HttpClientErrorException', 'RuntimeException', 'RemoteException',
                          'UnknownHostException', 'ExceptionTranslator', 'ExceptionTranslationFilter',
                          'NullPointerException',
                          'NoSuchPageException']
        exceptions_found = ""
        for e in exception_list:
            if e in line:
                exceptions_found = exceptions_found + e + ", "
        return exceptions_found[:-2]

    def verifyErrorCode(line):
        error_code_list = [' 401', ' 404', ' 500']
        error_codes = ""
        for ec in error_code_list:
            if ec in line:
                error_codes = ec[1:]
        return error_codes

    def verifyError(line):
        listError = ['transport error', 'DefaultResponseErrorHandler']
        er = ""
        for error in listError:
            if error in line:
                er = error
        return er

    def verifyWarning(line):
        warning_list = ['WARN', 'WARN 1']
        warning = ""
        for w in warning_list:
            if w in line:
                warning = w
        return warning

    def verifyFailure(line):
        failure_list = ['fail', 'Failure']
        failure = ""
        for f in failure_list:
            if f in line:
                failure = f
        return failure

    def generate_message(checkException, checkFailure, checkError, checkErrorCode, checkWarning, line_number,
                         timestamp):
        message = 'Date:\t' + timestamp + '\n\n' + \
                  "Line Number:\t" + line_number + '\n' + \
                  "Exception Type:\t" + checkException + '\n' + \
                  "Failure Type:\t" + checkFailure + '\n' + \
                  "Error Type:\t\t" + checkError + '\n' + \
                  "Error Code:\t\t" + checkErrorCode + '\n' + \
                  "Warning Type:\t" + checkWarning + '\n\n'
        return message

    # Key for all the error
    master_error_list = ['AccessDeniedException', 'HttpClientErrorException', 'RuntimeException', 'RemoteException',
                         'UnknownHostException', 'ExceptionTranslator', 'ExceptionTranslationFilter',
                         'NullPointerException',
                         'NoSuchPageException', 'transport error', 'DefaultResponseErrorHandler', 'WARN', 'WARN 1',
                         '401', '404', '500']

    master_controller_list = ['DockerServerController', 'DockerVolumeController', 'ProvisionController',
                              'BlueprintController']

    # Create new key for dictionary base on list of Error
    for i in master_error_list:
        if i not in dictionary.keys():
            dictionary[i] = []

    for i in master_controller_list:
        if i not in usage_dictionary.keys():
            usage_dictionary[i] = []

    # Not used???
    length = len(master_error_list)

    checkHour = ''
    # List of all dates found in the log
    listDateHour = []
    listHour = []

    # Loop for parsing through log lines
    for line in logfile:
        line_number = line_number + 1

        try:
            t_stamp_index = line.index('hfvm') - 1
            timestamp = line[:t_stamp_index]

            currentHour = ''
            # Aug 20
            # currentDate = timestamp[0:6]
            # Aug 20 06
            currentHour = timestamp[:9]

            # Only add a new date per hour count if it doesn't exist yet
            # EX: Aug 20 06, Aug 20 07...
            if currentHour != checkHour or checkHour == '':
                # EX: Aug 20 06
                checkHour = currentHour
                listDateHour.append(checkHour)

            # I don't think this is safe. Mine is not very safe either LOL.
            # timestamp = line[0:15]

            checkError = verifyError(line)
            checkException = verifyException(line)
            checkFailure = verifyFailure(line)
            checkErrorCode = verifyErrorCode(line)
            checkWarning = verifyWarning(line)
            checkController = verifyController(line)

            if not checkController:
                checkController = 'None'

            controller_message = 'Date:\t' + timestamp + '\n\n' + \
                                 "Controll type: " + checkController + "\n"

            if checkController != 'None':
                for i in master_controller_list:
                    if i in checkController:
                        usage_dictionary[i].append(controller_message)

            if not checkException:
                checkException = 'None'
            if not checkFailure:
                checkFailure = 'None'
            if not checkError:
                checkError = 'None'
            if not checkErrorCode:
                checkErrorCode = 'None'
            if not checkWarning:
                checkWarning = 'None'

            message = generate_message(checkException, checkFailure, checkError, checkErrorCode, checkWarning,
                                       str(line_number), timestamp)

            if checkFailure != 'None' or checkWarning != "None" or checkException != 'None' or checkError != 'None' or checkErrorCode != 'None':
                for i in master_error_list:
                    if i in checkException:
                        dictionary[i].append(message)
                    if i in checkFailure:
                        dictionary[i].append(message)
                    if i in checkErrorCode:
                        dictionary[i].append(message)
                    if i in checkError:
                        dictionary[i].append(message)
                    if i in checkWarning:
                        dictionary[i].append(message)
        except ValueError:
            pass

    # print 'listDateHour contents: ', listDateHour

    if os.path.exists('getcontroller.csv'):
        controller_attributes = []
        controller_attributes.append('Date')

        controller_volume = []
        csv = open('getcontroller.csv', 'a')

        time_key = listDateHour[0].capitalize()

        for controller_key in usage_dictionary:
            if usage_dictionary[controller_key]:
                count_hour = 1
                count = 0
                controller_attributes.append(controller_key)
                controller_volume.append(count)

                for data in usage_dictionary[controller_key]:
                    get_hour = data[6:15]

                    if get_hour != time_key:
                        count_hour = count_hour + 1
                        time_key = get_hour
                        count = 0
                        count = count + 1
                        controller_volume.append(count)
                    else:
                        count = count + 1
                        controller_volume[len(controller_volume) - 1] = count
                while count_hour < len(listDateHour):
                    controller_volume.append(0)
                    count_hour = count_hour + 1
                time_key = listDateHour[0].capitalize()

        string1 = ''
        string2 = ''

        for i in controller_attributes:
            string1 = string1 + i + ','

        csv.writelines('\n')
        csv.writelines('itemID: ' + str(item_pk))
        csv.writelines('\n')
        csv.writelines(string1[:-1])

        for ele in xrange(len(listDateHour)):
            j = ele

            formatDate = '2017-' + listDateHour[ele][:3] + '-' + listDateHour[ele][4:6] + ' ' + listDateHour[ele][
                                                                                                7:] + 'H'
            csv.writelines('\n' + formatDate + ',')
            valid = True
            while j < len(controller_volume):
                if (valid == True):
                    string2 = string2 + str(controller_volume[j]) + ","
                    valid = False
                else:
                    string2 = string2 + str(controller_volume[j]) + ","
                j = j + len(listDateHour)
            csv.writelines(string2[:-1])
            string2 = ''

        csv.close()

    else:
        # Date,WARN,RuntimeException,transport error,AccessDeniedException,404,UnknownHostException,RemoteException...
        controller_attributes = []
        controller_attributes.append('Date')
        # 18-Aug-17,8,8,35,20,41,24,24...
        controller_volume = []
        csv = open('getcontroller.csv', 'w')

        time_key = listDateHour[0].capitalize()
        # Loops through all keys in the dictionary, Aug 20 06, Aug 20 07, etc.
        for controller_key in usage_dictionary:
            # str12 = error_key
            # If values for key is not empty
            if usage_dictionary[controller_key]:
                count_hour = 1  # Count of the hour is 1, it only appears once so far
                count = 0  # Volume count of a given error is initialized as 0.
                controller_attributes.append(controller_key)  # Add the error key, Date,WARN, etc.
                controller_volume.append(count)  # Add the error volume for a given error key. 18-Aug-17,8,8, etc.
                # Loop through the list of error volumes for the key
                for data in usage_dictionary[controller_key]:
                    # get_hour gets the date (ex: Aug 20 06)
                    get_hour = data[6:15]

                    # If date found in dictionary is different from the date list's date
                    # Maybe it's hardcoded for 2 days. We only compare it to listDateHour[0]
                    if get_hour != time_key:
                        # Different date
                        count_hour = count_hour + 1
                        time_key = get_hour
                        count = 0
                        count = count + 1
                        controller_volume.append(count)
                    else:
                        count = count + 1
                        # Set the latest error volume as the count,
                        # 18-Aug-17,8,8,35,20,41,24,24...16,[17]
                        controller_volume[len(controller_volume) - 1] = count
                while count_hour < len(listDateHour):
                    controller_volume.append(0)
                    count_hour = count_hour + 1
                time_key = listDateHour[0].capitalize()

        # string01 = attributes to write to CSV: Date,WARN,RuntimeException,transport error...
        string1 = ''
        # string02 = volume of said attributes: 2017-Aug-20 06H,1,8,7,...
        string2 = ''
        # Gets all error volumes found in log for a given day
        for i in controller_attributes:
            string1 = string1 + i + ','
        csv.writelines('\n')
        # Write to CSV, itemID: 34...
        csv.writelines('itemID: ' + str(item_pk))
        csv.writelines('\n')
        # Write to CSV, line = 18-Aug-17,0,0,...0
        csv.writelines(string1[:-1])

        # for i = 0; i < # of hours found in the log
        for ele in xrange(len(listDateHour)):
            j = ele
            # listDateHour format: Aug 20 06
            # formatDate = str(listDateHour[ele][4:6]) + '-' + listDateHour[ele][0:3] + '-2017'
            formatDate = '2017-' + listDateHour[ele][:3] + '-' + listDateHour[ele][4:6] + ' ' + listDateHour[ele][
                                                                                                7:] + 'H'
            # print 'happen 2'
            # Write to CSV, line = 20-Aug-2017,
            csv.writelines('\n' + formatDate + ',')
            valid = True
            # listDateHour = Aug 20 06, Aug 20 07...
            # errorVolume = Aug 20 06,0,1,3,2...
            # j will always be less than size of listDateHour
            while j < len(controller_volume):
                if (valid == True):
                    string2 = string2 + str(controller_volume[j]) + ","
                    valid = False
                else:
                    string2 = string2 + str(controller_volume[j]) + ","
                j = j + len(listDateHour)
            csv.writelines(string2[:-1])
            string2 = ''

        csv.close()

    # Transfer analyzed data to new CSV file
    if os.path.exists('getdata.csv'):

        # Date,WARN,RuntimeException,transport error,AccessDeniedException,404,UnknownHostException,RemoteException...
        error_attributes = []
        error_attributes.append('Date')
        # 18-Aug-17,8,8,35,20,41,24,24...
        error_volume = []
        csv = open('getdata.csv', 'a')

        time_key = listDateHour[0].capitalize()
        # Loops through all keys in the dictionary, Aug 20 06, Aug 20 07, etc.
        for error_key in dictionary:
            # str12 = error_key
            # If values for key is not empty
            if dictionary[error_key]:
                count_hour = 1  # Count of the hour is 1, it only appears once so far
                count = 0  # Volume count of a given error is initialized as 0.
                error_attributes.append(error_key)  # Add the error key, Date,WARN, etc.
                error_volume.append(count)  # Add the error volume for a given error key. 18-Aug-17,8,8, etc.
                # Loop through the list of error volumes for the key
                for data in dictionary[error_key]:
                    # get_hour gets the date (ex: Aug 20 06)
                    get_hour = data[6:15]

                    # If date found in dictionary is different from the date list's date
                    # Maybe it's hardcoded for 2 days. We only compare it to listDateHour[0]
                    if get_hour != time_key:
                        # Different date
                        count_hour = count_hour + 1
                        time_key = get_hour
                        count = 0
                        count = count + 1
                        error_volume.append(count)
                    else:
                        count = count + 1
                        # Set the latest error volume as the count,
                        # 18-Aug-17,8,8,35,20,41,24,24...16,[17]
                        error_volume[len(error_volume) - 1] = count
                while count_hour < len(listDateHour):
                    error_volume.append(0)
                    count_hour = count_hour + 1
                time_key = listDateHour[0].capitalize()

        string01 = ''
        string02 = ''
        # Gets all error volumes found in log for a given day
        for i in error_attributes:
            string01 = string01 + i + ','
        csv.writelines('\n')
        # Write to CSV, itemID: 34...
        csv.writelines('itemID: ' + str(item_pk))
        csv.writelines('\n')
        # Write to CSV, line = 18-Aug-17,0,0,...0
        csv.writelines(string01[:-1])

        # for i = 0; i < # of hours found in the log
        for ele in xrange(len(listDateHour)):
            j = ele
            # listDateHour format: Aug 20 06
            # formatDate = str(listDateHour[ele][4:6]) + '-' + listDateHour[ele][0:3] + '-2017'
            formatDate = '2017-' + listDateHour[ele][:3] + '-' + listDateHour[ele][4:6] + ' ' + listDateHour[ele][
                                                                                                7:] + 'H'
            # print 'happen 2'
            # Write to CSV, line = 20-Aug-2017,
            csv.writelines('\n' + formatDate + ',')
            valid = True
            while j < len(error_volume):
                if (valid == True):
                    string02 = string02 + str(error_volume[j]) + ","
                    valid = False
                else:
                    string02 = string02 + str(error_volume[j]) + ","
                j = j + len(listDateHour)
            csv.writelines(string02[:-1])
            string02 = ''

        csv.close()

    # CSV does not exist
    else:

        # Date,WARN,RuntimeException,transport error,AccessDeniedException,404,UnknownHostException,RemoteException...
        error_attributes = []
        error_attributes.append('Date')
        # 18-Aug-17,8,8,35,20,41,24,24...
        error_volume = []
        csv = open('getdata.csv', 'w')

        time_key = listDateHour[0].capitalize()
        # Loops through all keys in the dictionary, Aug 20 06, Aug 20 07, etc.
        for error_key in dictionary:
            # str12 = error_key
            # If values for key is not empty
            if dictionary[error_key]:
                count_hour = 1  # Count of the hour is 1, it only appears once so far
                count = 0  # Volume count of a given error is initialized as 0.
                error_attributes.append(error_key)  # Add the error key, Date,WARN, etc.
                error_volume.append(count)  # Add the error volume for a given error key. 18-Aug-17,8,8, etc.
                # Loop through the list of error volumes for the key
                for data in dictionary[error_key]:
                    # get_hour gets the date (ex: Aug 20 06)
                    get_hour = data[6:15]

                    # If date found in dictionary is different from the date list's date
                    # Maybe it's hardcoded for 2 days. We only compare it to listDateHour[0]
                    if get_hour != time_key:
                        # Different date
                        count_hour = count_hour + 1
                        time_key = get_hour
                        count = 0
                        count = count + 1
                        error_volume.append(count)
                    else:
                        count = count + 1
                        # Set the latest error volume as the count,
                        # 18-Aug-17,8,8,35,20,41,24,24...16,[17]
                        error_volume[len(error_volume) - 1] = count
                while count_hour < len(listDateHour):
                    error_volume.append(0)
                    count_hour = count_hour + 1
                time_key = listDateHour[0].capitalize()

        # string01 = attributes to write to CSV: Date,WARN,RuntimeException,transport error...
        string01 = ''
        # string02 = volume of said attributes: 2017-Aug-20 06H,1,8,7,...
        string02 = ''
        # Gets all error volumes found in log for a given day
        for i in error_attributes:
            string01 = string01 + i + ','
        csv.writelines('\n')
        # Write to CSV, itemID: 34...
        csv.writelines('itemID: ' + str(item_pk))
        csv.writelines('\n')
        # Write to CSV, line = 18-Aug-17,0,0,...0
        csv.writelines(string01[:-1])

        # for i = 0; i < # of hours found in the log
        for ele in xrange(len(listDateHour)):
            j = ele
            # listDateHour format: Aug 20 06
            # formatDate = str(listDateHour[ele][4:6]) + '-' + listDateHour[ele][0:3] + '-2017'
            formatDate = '2017-' + listDateHour[ele][:3] + '-' + listDateHour[ele][4:6] + ' ' + listDateHour[ele][
                                                                                                7:] + 'H'
            # print 'happen 2'
            # Write to CSV, line = 20-Aug-2017,
            csv.writelines('\n' + formatDate + ',')
            valid = True
            # listDateHour = Aug 20 06, Aug 20 07...
            # errorVolume = Aug 20 06,0,1,3,2...
            # j will always be less than size of listDateHour
            while j < len(error_volume):
                if (valid == True):
                    string02 = string02 + str(error_volume[j]) + ","
                    valid = False
                else:
                    string02 = string02 + str(error_volume[j]) + ","
                j = j + len(listDateHour)
            print 'happen 3'
            csv.writelines(string02[:-1])
            string02 = ''

        csv.close()

    # After writing to CSV, work on time-series graph
    print str(current_user_id) + "check current user ID at line 402"
    time_series_csv = 'user_' + str(current_user_id) + '_time_series' + ".csv"
    if os.path.exists(time_series_csv):
        print str(current_user_id) + "check current user ID at line 405"
        print 'Time series csv exists.'
        add_time_series(time_series_csv, 'getdata.csv', 'a', current_user_id)
    else:
        print str(current_user_id) + "check current user ID at line 409"
        print 'Time series csv does not exist'
        add_time_series(time_series_csv, 'getdata.csv', 'w', current_user_id)


def convertDate(get_date):
    # listDate1
    # 2017-Aug-20 06H,0,0,0,0,1,0,0,0,0
    # listDate2
    # 2017-Aug-20 07H,14,6,1,2,21,7,7,24,14

    # date = string_data[0].split('-')


    day = get_date[8:10]
    year = get_date[:4]
    hour = get_date[10:]

    month_list = {"01": 'Jan', "02": 'Feb', "03": 'Mar', "04": 'Apr', "05": 'May', "06": 'Jun', "07": 'Jul',
                  "08": "Aug",
                  "09": 'Sep', "10": 'Oct', "11": "Nov", "12": "Dec"}
    try:
        month = str(month_list[get_date[5:7]])
    except:
        print 'Bad month format, month string is not 3 characters long or is not capitalized.'
        return None

    newDate = year + '-' + month + '-' + day + hour
    get_date = newDate
    return get_date


def convert_from_data_to_time(attributes, volume):
    # Attributes = Date,WARN,WARN 1,RuntimeException,transport error,AccessDeniedException...
    # Volume = 2017-Aug-22 06H,0,0,0,0,0,0,0,0,0,0,0,0
    master_error_list = ['AccessDeniedException', 'HttpClientErrorException', 'RuntimeException', 'RemoteException',
                         'UnknownHostException', 'ExceptionTranslator', 'ExceptionTranslationFilter',
                         'NullPointerException',
                         'NoSuchPageException', 'transport error', 'DefaultResponseErrorHandler', 'WARN', 'WARN 1',
                         '401', '404', '500']

    data_to_time_volume = list()
    attributes_without_date = attributes[1:]
    volume_without_date = volume[1:]

    for i in range(len(master_error_list)):
        attribute_in_day = False
        for j in range(len(attributes_without_date)):
            if master_error_list[i] == attributes_without_date[j]:
                attribute_in_day = True
                data_to_time_volume.append(str(volume_without_date[j]))
                break
        if not attribute_in_day:
            data_to_time_volume.append('0')

    return volume[0] + ',' + ','.join(data_to_time_volume)


def add_time_series(destination, source, mode, current_user_id):
    print str(current_user_id) + 'check current user ID at add_time_series'
    time_series_filename = 'user_' + str(user_id) + '_time_series' + ".csv"

    time_series_csv = open(destination, mode)
    atItemID = False
    itemID_line = 'itemID: ' + str(item_pk)
    attributes = list()

    with open(source) as file:
        for line in file:
            if (not atItemID) and line.rstrip('\n') == itemID_line:
                atItemID = True
            elif atItemID and line.startswith('Date'):
                # Date,WARN,WARN 1,RuntimeException,transport error...
                attributes = line.rstrip('\n').split(',')
            elif atItemID and not line.rstrip('\n') == '' and not line.startswith('itemID'):
                # 2017-Aug-22 07H,6,6,1,2,8,1,3,9,9,3,3,1
                # Need to convert first
                volume = line.rstrip('\n').split(',')
                time_series_csv.write(convert_from_data_to_time(attributes, volume) + '\n')
                # lines.append(line.rstrip('\n'))
            elif atItemID and (line.startswith('itemID') or line.rstrip('\n') == ''):
                # No longer at the file to look at.
                # print 'Line to break ', line.rstrip('\n')
                # atItemID = False
                break

    time_series_csv.close()

    sort_and_merge_time_series_csv(time_series_filename)


def sort_and_merge_time_series_csv(filename):
    lines = list()
    print filename + '???????????????????????????????????????????????????'
    with open(filename) as file:
        for line in file:
            lines.append(line.rstrip('\n'))
    lines.sort()

    # print 'Old time series: '
    # for line in lines:
    #     print line

    new_lines = list()
    new_lines_index = -1
    prev_timestamp = ''
    for i in range(len(lines)):
        # 2017-Aug-20 06H
        current_timestamp = lines[i][:15]
        # Multiple instances of 2017-Aug-20 06H
        if prev_timestamp == current_timestamp:
            # print 'Old line: ', lines[i - 1]
            # print 'New line: ', lines[i]
            # Get the old line, we're going to update it.
            old_line = new_lines[new_lines_index][16:].split(',')
            # print 'Old split by commas: ', old_line
            # Split the error volumes.
            new_line = lines[i][16:].split(',')
            # Add the error volumes from the new line to the old line.
            for j in range(len(old_line)):
                old_line[j] = str(int(old_line[j]) + int(new_line[j]))
            updated_old_line = prev_timestamp + ',' + ','.join(old_line)
            # print 'Added new line to old line: ', updated_old_line
            # Replace old line
            new_lines[new_lines_index] = updated_old_line
        # Previous line is 2017-Aug-20 06H, current = 2017-Aug-20 07H
        else:
            new_lines.append(lines[i])
            new_lines_index += 1

        prev_timestamp = current_timestamp

    # print 'New time series:'
    # for line in new_lines:
    #     print line

    os.remove(filename)
    if not os.path.exists(filename):
        csv = open(filename, 'w')
        for line in new_lines:
            csv.writelines(line + '\n')
        csv.close()


def unmerge_time_series_csv(destination, source, itemID_to_delete):
    lines = list()
    with open(destination) as file:
        for line in file:
            lines.append(line.rstrip('\n'))

    atItemID = False
    # itemID_line = 'itemID: ' + str(itemID_to_delete)
    attributes = list()

    with open(source) as file:
        for line in file:
            if (not atItemID) and line.rstrip('\n') == itemID_to_delete:
                # print '1 ', line.rstrip('\n')
                atItemID = True
            elif atItemID and not line.startswith('Date') and not line.startswith('itemID'):
                # 2017-Aug-22 07H,6,6,1,2,8,1,3,9,9,3,3,1
                # Need to convert first
                # print '2 ', line.rstrip('\n')
                volume = line.rstrip('\n').split(',')
                lines.append(convert_from_data_to_time(attributes, volume))
                # lines.append(line.rstrip('\n'))
            elif atItemID and line.startswith('Date'):
                # Date,WARN,WARN 1,RuntimeException,transport error...
                # print '3 ', line.rstrip('\n')
                attributes = line.rstrip('\n').split(',')
            elif atItemID and (line.startswith('itemID') or line.rstrip('\n') == ''):
                # No longer at the file to look at.
                # print 'Line to break ', line.rstrip('\n')
                # atItemID = False
                break

    lines.sort(reverse=True)

    # print 'Old time series: '
    # for line in lines:
    #     print line

    new_lines = list()
    new_lines_index = -1
    prev_timestamp = ''
    for i in range(len(lines)):
        # 2017-Aug-20 06H
        current_timestamp = lines[i][:15]
        # Multiple instances of 2017-Aug-20 06H
        if prev_timestamp == current_timestamp:
            # print 'Old line: ', lines[i - 1]
            # print 'New line: ', lines[i]
            # Get the old line, we're going to update it.
            old_line = new_lines[new_lines_index][16:].split(',')
            # print 'Old split by commas: ', old_line
            # Split the error volumes.
            new_line = lines[i][16:].split(',')
            # Subtract the error volumes from the new line to the old line.
            for j in range(len(old_line)):
                print old_line[j]
                print new_line[j]
                new_volume_count = int(old_line[j]) - int(new_line[j])
                if new_volume_count < 0:
                    pass
                old_line[j] = str(new_volume_count)
            updated_old_line = prev_timestamp + ',' + ','.join(old_line)
            # print 'Subtracted new line to old line: ', updated_old_line
            # Replace old line
            new_lines[new_lines_index] = updated_old_line
        # Previous line is 2017-Aug-20 06H, current = 2017-Aug-20 07H
        else:
            new_lines.append(lines[i])
            new_lines_index += 1

        prev_timestamp = current_timestamp

    new_lines.sort()

    os.remove(destination)
    if not os.path.exists(destination):
        csv = open(destination, 'w')
        for line in new_lines:
            if not all(v == '0' for v in line[16:].split(',')):
                csv.writelines(line + '\n')
        csv.close()


####################### Item Part ###############################

def add_item_to_folder(request, pk):
    print "add item 1"
    folder = get_object_or_404(Folder, pk=pk)
    # get upload item here
    for fi in request.FILES:
        global file_up_name
        file_up_name = str(dict(request.FILES)[fi][0])
        print file_up_name

    form = ItemForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        print "add item 4"
        item = form.save(commit=False)
        item.folder = folder
        item.save()
        global item_pk
        item_pk = str(item.pk)
        return redirect('folder_detail', pk=folder.pk)
    else:
        print "add item 2"
        form = ItemForm()

    print "add item 3"
    return render(request, 'folder/item_form.html', {'form': form})


def item_approve(request, pk):
    item = get_object_or_404(Item, pk=pk)
    item.approve()
    print str(request.user.id) + 'asdasdadasdasdadasdasdasdsadasdas'
    # will do analyze part here after approved the file
    # analyzed()
    global user_id
    user_id = request.user.id
    data(user_id)

    print file_up_name + "-Check"
    # need to remove file in server after analyzed file here
    str1 = ''
    count = 0
    if ' ' in file_up_name:
        for word in file_up_name.split(" "):
            if count == 0:
                str1 = str1 + word
                count = 1
            else:
                str1 = str1 + '_' + word
        os.remove(str1)
    else:
        os.remove(file_up_name)

    # os.remove(filename) file name must be change if it have space
    print "approved"
    return redirect('folder_detail', pk=item.folder.pk)


def item_remove(request, pk):
    global user_id
    user_id = request.user.id
    str1 = ''
    count = 0
    if os.path.exists(file_up_name):
        if ' ' in file_up_name:
            for word in file_up_name.split(" "):
                if count == 0:
                    str1 = str1 + word
                    count = 1
                else:
                    str1 = str1 + '_' + word
            os.remove(str1)
        else:
            os.remove(file_up_name)
    time_series_filename = 'user_' + str(user_id) + '_time_series' + ".csv"
    itemID_to_delete = 'itemID: ' + str(pk)
    unmerge_time_series_csv(time_series_filename, 'getdata.csv', itemID_to_delete)
    item = get_object_or_404(Item, pk=pk)
    folder_pk = item.folder.pk
    item.delete()
    return redirect('folder_detail', pk=folder_pk)


# def item_remove(request, pk):
#     global user_id
#     user_id = request.user.id
#     str1 = ''
#     count = 0
#     if os.path.exists(file_up_name):
#         if ' ' in file_up_name:
#             for word in file_up_name.split(" "):
#                 if count == 0:
#                     str1 = str1 + word
#                     count = 1
#                 else:
#                     str1 = str1 + '_' + word
#             os.remove(str1)
#         else:
#             os.remove(file_up_name)
#     time_series_filename = 'user_' + str(user_id) + '_time_series' + ".csv"
#     unmerge_time_series_csv(time_series_filename)
#     item = get_object_or_404(Item, pk=pk)
#     folder_pk = item.folder.pk
#     item.delete()
#     return redirect('folder_detail', pk=folder_pk)


##################### Chart ########################################

class ItemChart(IndexView):
    print 'get-data-4'
    template_name = 'folder/chart.html'

    def get(self, request, *args, **kwargs):
        print 'get-data-5'
        line = str(request)
        first_temp = line.index('/chart/')
        item_primary_key = line[first_temp + 7:-2]
        global check_item_pk
        check_item_pk = item_primary_key
        # print item_primary_key

        return render(request, self.template_name, {})


def get_data(request, *args, **kwargs):
    data = {
        "sales": 100,
        "customers": 10,
    }
    print "get-data"
    return JsonResponse(data)  # http response


# def get_data_info(data_info):
#     str_arr = []
#     if 'Date' not in data_info:
#         print False
#         for word in xrange(len(data_info)):
#             if word > 0:
#                 str_arr.append(int(data_info[word]))
#     else:
#         print True
#         for word in xrange(len(data_info)):
#             print word
#             if word > 0:
#                 str_arr.append(data_info[word])
#                 print str_arr
#
#     return str_arr

class ChartData(APIView):
    print 'get-data-2'
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None, ):
        print request
        print 'get-data-3'

        count = 0
        list_error = ''
        all_data = []
        valid = False

        ccount = 0
        list_controller = ''
        all_controller = []
        cvalid = False

        file_data = open('getdata.csv', 'r')

        for csv_line in file_data:
            got = intern(str('itemID: ' + str(check_item_pk) + '\n'))
            checked = intern(str(csv_line))
            if got is checked or valid == True:
                valid = True
                if count > 0:
                    if count == 1:
                        list_error = csv_line.split(',')
                    else:
                        if "itemID:" in csv_line:
                            break
                        else:
                            all_data.append(csv_line.split(','))
                count = count + 1

        total_volume = [0] * len(list_error)

        for i in xrange(len(all_data)):
            # print i
            for j in xrange(len(all_data[i])):
                if j != 0:
                    total_volume[j] = int(total_volume[j]) + int(all_data[i][j])

        file_controller = open('getcontroller.csv', 'r')

        for csv_line in file_controller:
            got = intern(str('itemID: ' + str(check_item_pk) + '\n'))
            checked = intern(str(csv_line))
            if got is checked or cvalid == True:
                cvalid = True
                if ccount > 0:
                    if ccount == 1:
                        list_controller = csv_line.split(',')
                    else:
                        if "itemID:" in csv_line:
                            break
                        else:
                            all_controller.append(csv_line.split(','))
                ccount = ccount + 1

        total_volume_controller = [0] * len(list_controller)
        if len(all_controller[len(all_controller) - 1]) > 2:
            for i in xrange(len(all_controller)):
                # print i
                for j in xrange(len(all_controller[i])):
                    if j != 0:
                        total_volume_controller[j] = int(total_volume_controller[j]) + int(all_controller[i][j])

        data = {
            'controllerlb': list_controller[1:],
            'controllervolume': total_volume_controller[1:],
            'controllerTotal': 'Controller Total',
            "labels": list_error[1:],
            "volume": total_volume[1:],
            "total": 'Total',
        }
        return Response(data)


###################### Time Series ##############################


class TimeSeries(IndexView):
    print 'Time Series 1'
    template_name = 'folder/time_series.html'

    def get(self, request, *args, **kwargs):
        print 'Time Series 2'
        global user_id
        user_id = request.user.id

        return render(request, self.template_name, {})


def get_time(request, *args, **kwargs):
    data = {
        "sales": 100,
        "customers": 10,
    }
    print "get-data"
    return JsonResponse(data)


class TimeSeriesData(APIView):
    def get(self, request, format=None, ):

        global user_id
        global start
        global end
        start_date = ""
        end_date = ""

        get_start_day = str(start)[:13] + "H"
        get_end_day = str(end)[:13] + "H"

        start_day = convertDate(get_start_day)
        end_day = convertDate(get_end_day)

        print start_day
        print end_day

        file_name = 'user_' + str(user_id) + '_time_series' + ".csv"
        print file_name
        lines = open(file_name, 'r')
        print "mo file"

        master_error_list = ['Date', 'AccessDeniedException', 'HttpClientErrorException', 'RuntimeException',
                             'RemoteException',
                             'UnknownHostException', 'ExceptionTranslator', 'ExceptionTranslationFilter',
                             'NullPointerException',
                             'NoSuchPageException', 'transport error', 'DefaultResponseErrorHandler', 'WARN', 'WARN 1',
                             '401', '404', '500']

        list_date = []

        for line in lines:
            string1 = line.split(',')
            list_date.append(string1)

        a = sorted(list_date, key=itemgetter(0))

        total = [0] * len(master_error_list)

        for i in xrange(len(list_date)):
            if i == 0:
                start_date = list_date[i][0]
            else:
                end_date = list_date[i][0]
            for j in xrange(len(list_date[i])):
                if j != 0:
                    total[j] = int(total[j]) + int(list_date[i][j])

        tolalwithindex = []
        for i in xrange(len(total)):
            listWithIndex = [total[i], i]
            tolalwithindex.append(listWithIndex)

        b = sorted(tolalwithindex, key=itemgetter(0))

        last_5 = b[12:]
        get_index_for_top_5 = []

        for i in last_5:
            get_index_for_top_5.append(i[1])

        errors = []
        dates = []
        first = []
        second = []
        third = []
        fourth = []
        fifth = []
        validDate = False


        for i in get_index_for_top_5:
            errors.append(master_error_list[i])

        countDay = 0

        if start_day != None:
            datearr1 = start_date.split("-")
            year1 = datearr1[0]
            month1 = datearr1[1]
            daytime1 = datearr1[2].split(" ")
            day1 = daytime1[0]
            times1 = daytime1[1]

            datearr2 = start_day.split("-")
            year2 = datearr2[0]
            month2 = datearr2[1]
            daytime2 = datearr2[2].split(" ")
            day2 = daytime2[0]
            times2 = daytime2[1]


            month_list = {"Jan": '01', "Feb": '02', "Mar": '03', "Apr": '04', "May": '05', "Jun": '06', "Jul": '07',
                          "Aug": "08",
                          "Sep": '09', "Oct": '10', "Nov": "11", "Dec": "12"}
            try:
                month1 = str(month_list[month1])
                month2 = str(month_list[month2])
            except:
                print 'Bad month format, month string is not 3 characters long or is not capitalized.'
                return None

            d1 = date(int(year1), int(month1), int(day1))
            d2 = date(int(year2), int(month2), int(day2))
            countDay = d2 - d1

            getTime = int(times2[:-1]) - int(times1[:-1])

            if int(countDay.days) < 0:
                validDate = True
            elif int(countDay.days) == 0:
                if getTime < 0:
                    validDate = True

        else:
            pass

        for i in xrange(len(a)):
            if str(a[i][0]) == str(start_day) or validDate == True:
                if str(a[i][0]) == str(end_day):
                    validDate = False
                    break

                validDate = True
                dates.append(a[i][0])
                for j in xrange(len(get_index_for_top_5)):
                    if j == 0:
                        first.append(a[i][get_index_for_top_5[j]])
                    elif j == 1:
                        second.append(a[i][get_index_for_top_5[j]])
                    elif j == 2:
                        third.append(a[i][get_index_for_top_5[j]])
                    elif j == 3:
                        fourth.append(a[i][get_index_for_top_5[j]])
                    else:
                        fifth.append(a[i][get_index_for_top_5[j]])
        data = {
            "ed": end_date,
            "sd": start_date,
            "dates": dates,
            "first": first,
            "second": second,
            "third": third,
            "fourth": fourth,
            "fifth": fifth,
            "error1": errors[0],
            "error2": errors[1],
            "error3": errors[2],
            "error4": errors[3],
            "error5": errors[4],

        }
        return Response(data)


###################### User #########################################


# class UserFormView(View):
#     form_class = UserForm
#     template_name = 'registration/register.html'
#
#     # display blank form
#     def get(self, request):
#         form = self.form_class(None)
#         return render(request, self.template_name, {'form': form})
#
#     # process form data
#     def post(self, request):
#         form = self.form_class(request.POST)
#
#         if form.is_valid():
#             user = form.save(commit=False)
#
#             # cleaned (normalize) data
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password1']
#
#             print 'something'
#
#             user.set_password(password)
#             user.save()
#
#             # return user objects if credentials are correct
#
#             user = authenticate(username = username, password = password)
#             login(request,user)
#
#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     return redirect('folder_list')
#
#         return render(request, self.template_name, {'form': form})


class UserRegisterFormView(View):
    form_class = RegistrationForm
    template_name = 'registration/register.html'

    # display blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    # process form data
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            # cleaned (normalize) data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            user.set_password(password)
            user.save()

            # return user objects if credentials are correct

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('folder_list')

        return render(request, self.template_name, {'form': form})


def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('folder_list')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {
        'form': form
    })


def DatePickerView(request):
    if request.method == 'POST':  # If the form has been submitted...
        form = DatePickerForm(request.POST)  # A form bound to the POST data
        if form.is_valid():  # All validation rules pass
            # get start day and end day here for draw the time series
            global start
            global end
            start = form.data.get('start')
            end = form.data.get('end')
            # TimeSeriesData()

            # will have a function here to college the data from the day that user provide
            return redirect('time_series')
    else:
        if request.GET.get('id', None):
            form = DatePickerForm(instance=DatePickerForm.objects.get(id=request.GET.get('id', None)))
        else:
            form = DatePickerForm()

    # return back to datepicker when the input not pass
    return render(request, 'folder/datepicker_form.html', {
        'form': form, 'bootstrap': 3
    })
