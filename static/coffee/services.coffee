#============================================================================
# Application services
#============================================================================

services = angular.module('cases.services', ['cases.modals']);


#=====================================================================
# Incoming message service
#=====================================================================
services.factory('MessageService', ['$rootScope', '$http', '$httpParamSerializer', ($rootScope, $http, $httpParamSerializer) ->
  new class MessageService

    #----------------------------------------------------------------------------
    # Fetches old messages for the given search
    #----------------------------------------------------------------------------
    fetchOld: (search, before, page) ->
      params = @_searchToParams(search)
      if !search.before
        params.before = utils.formatIso8601(before)
      params.page = page
      return $http.get('/message/search/?' + $httpParamSerializer(params)).then((response) ->
        utils.parseDates(response.data.results, 'time')
        return {results: response.data.results, hasMore: response.data.has_more}
      )

    #----------------------------------------------------------------------------
    # Fetches history for a single message
    #----------------------------------------------------------------------------
    fetchHistory: (message) ->
      return $http.get('/message/history/' + message.id + '/').then((response) ->
        return utils.parseDates(response.data.actions, 'created_on')
      )

    #----------------------------------------------------------------------------
    # Starts a message export
    #----------------------------------------------------------------------------
    startExport: (search) ->
      return $http.post('/messageexport/create/?' + $httpParamSerializer(@_searchToParams(search)))

    #----------------------------------------------------------------------------
    # Reply-to messages
    #----------------------------------------------------------------------------
    bulkReply: (messages, text) ->
      params = {text: text, messages: (m.id for m in messages)}

      return $http.post('/message/bulk_reply/', params)

    #----------------------------------------------------------------------------
    # Flag or un-flag messages
    #----------------------------------------------------------------------------
    bulkFlag: (messages, flagged) ->
      action = if flagged then 'flag' else 'unflag'

      return @_bulkAction(messages, action, null).then(() ->
        for msg in messages
          msg.flagged = flagged
      )

    #----------------------------------------------------------------------------
    # Label messages with the given label
    #----------------------------------------------------------------------------
    bulkLabel: (messages, label) ->
      return @_bulkAction(messages, 'label', label).then(() ->
        for msg in messages
          if label not in msg.labels
            msg.labels.push(label)
      )

    #----------------------------------------------------------------------------
    # Archive messages
    #----------------------------------------------------------------------------
    bulkArchive: (messages) ->
      return @_bulkAction(messages, 'archive', null).then(() ->
        for msg in messages
          msg.archived = true
      )

    #----------------------------------------------------------------------------
    # Restore (i.e. un-archive) messages
    #----------------------------------------------------------------------------
    bulkRestore: (messages) ->
      return @_bulkAction(messages, 'restore', null).then(() ->
        for msg in messages
          msg.archived = false
      )

    #----------------------------------------------------------------------------
    # Relabel the given message (removing labels if necessary)
    #----------------------------------------------------------------------------
    relabel: (message, labels) ->
      params = {labels: (l.id for l in labels)}

      return $http.post('/message/label/' + message.id + '/', params).then(() ->
        message.labels = labels
      )

    #----------------------------------------------------------------------------
    # Forward a message to a URN
    #----------------------------------------------------------------------------
    forward: (message, text, urn) ->
      params = {text: text, urns: [urn.urn]}

      return $http.post('/message/forward/' + message.id + '/', params)

    #----------------------------------------------------------------------------
    # Convert search object to URL params
    #----------------------------------------------------------------------------
    _searchToParams: (search) ->
      return {
        folder: search.folder,
        text: search.text,
        after: utils.formatIso8601(search.after),
        before: utils.formatIso8601(search.before),
        groups: if search.groups then (g.uuid for g in search.groups) else null,
        contact: if search.contact then search.contact.id else null,
        label: if search.label then search.label.id else null,
        archived: if search.archived then 1 else 0
      }

    #----------------------------------------------------------------------------
    # POSTs to the messages bulk action endpoint
    #----------------------------------------------------------------------------
    _bulkAction: (messages, action, label) ->
      params = {messages: (m.id for m in messages)}
      if label
        params.label = label.id

      return $http.post('/message/action/' + action + '/', params)
])

#=====================================================================
# Frequently Asked Question Replies service
#=====================================================================
services.factory('FAQService', ['$rootScope', '$http', '$httpParamSerializer', ($rootScope, $http, $httpParamSerializer) ->
  new class FAQService

    #----------------------------------------------------------------------------
    # Fetches replies to FAQs
    #----------------------------------------------------------------------------

    fetchFaqs: (search) ->
      # Dummy results; to be removed when API ready
      results = [{
          "id": 1,
          "question": "Can I get infected from touching an HIV+ person's blood ?",
          "answer": "Contact with an HIV+'s blood may lead to infection . Please contact 0865000342 for for urgent assistance if you may have conme into contact with an HIV+'s blood",
          "labels": [
              {'id': 12, 'name': "AIDS"}
          ]
      },
      {
          "id": 2,
          "question": "Can my baby also be HIV+ ?",
          "answer": "It depends on wether you had used the Vital B medication prescribed to pregnant mothers.",
          "labels": [
              {'id': 12, 'name': "HIV"},
              {'id': 15, 'name': "Pregnancy"}
          ]
        },
        {
          "id": 2,
          "question": "Must I close the windows if I have TB ?",
          "answer": "Please be advised all windows are to be kept open at all times",
          "labels": [
              {'id': 13, 'name': "TB"}
          ]
        },
        {
          "id": 2,
          "question": "How will I know If I am pregnant ?",
          "answer": "Please visit www.amipregnant.com",
          "labels": [
              {'id': 15, 'name': "Pregnancy"}
          ]
        },
        {
          "id": 2,
          "question": "example question 5",
          "answer": "example answer 5",
          "labels": [
              {'id': 102, 'name': "TB"},
              {'id': 103, 'name': "Pregnancy"},
          ]
        },
        {
          "id": 2,
          "question": "example question 6",
          "answer": "example answer 6",
          "labels": [
              {'id': 102, 'name': "TB"},
              {'id': 103, 'name': "Pregnancy"},
          ]
        },
        {
          "id": 11,
          "question": "Will my child get Ebola if I'm HIV positive ?",
          "answer": "No , your child will not get Ebola , unless he/she is exposed to the virus",
          "labels": [
              {'id': 15, 'name': "HIV"}

          ]
        },
        {
          "id": 13,
          "question": "Bablo selesa ikomu saniolo Ebola bu HIV positive lesa?",
          "answer": "Manase roja bokolo ya virus sleyona mkonena wer wer vetar",
          "labels": [
              {'id': 15, 'name': "HIV"}

          ]
        },
        {
          "id": 6,
          "question": "Nkri nkri boro wayelsa ?",
          "answer": "Machukana e natenda www.amipregnat.com  vaeslav",
          "labels": [
              {'id': 13, 'name': "Pregnancy"},
          ]
          }
      ]
      if search.label
        if search.label.name == 'TB'
          results = [results[2]]
        else if search.label.name == 'HIV'
          if search.text
            if search.text.toLowerCase() == "ebola"
              if search.language == 3
                results = [results[7]]
              else
                results = [results[6]]

            else
              results = [results[0],results[1]]
        else
          if search.language == 3
            results =[results[8]]
          else
            results = [results[3],results[4],results[5]]
      else
        results

      # Comment out when API ready
      # params = @_searchFaqsToParams(search)
      # return $http.get('/faq/search/?'+$httpParamSerializer(params)).then((response) -> response.data.results)
      results

    #----------------------------------------------------------------------------
    # Convert search object to URL params
    #----------------------------------------------------------------------------
    _searchFaqsToParams: (search) ->
      return {
        text: search.text,
        label: if search.label then search.label.id else null
      }
])

#=====================================================================
# Language service
#=====================================================================
services.factory('LanguageService', ['$rootScope', '$http', ($rootScope, $http, $httpParamSerializer) ->
  new class LanguageService
      getLanguages : () ->
          # COMMENT OUT WHEN API READY
          # return $http.get('/lang).then((response) -> response.data.results)
          dummy_languages = [{
            id:1,
            name:'English Nigeria',
            code:'eng_ng'
          },
          {
            id:2,
            name:'English South Africa',
            code:'eng_za'
          },
          {
            id:3,
            name:'French Nigeria',
            code:'fr_ng'
          }]
          return dummy_languages


  ])

#=====================================================================
# Incoming message service
#=====================================================================
services.factory('OutgoingService', ['$rootScope', '$http', '$httpParamSerializer', ($rootScope, $http, $httpParamSerializer) ->
  new class OutgoingService

    #----------------------------------------------------------------------------
    # Fetches old outgoing messages for the given search
    #----------------------------------------------------------------------------
    fetchOld: (search, startTime, page) ->
      params = @_outboxSearchToParams(search, startTime, page)

      return $http.get('/outgoing/search/?' + $httpParamSerializer(params)).then((response) ->
        utils.parseDates(response.data.results, 'time')
        return {results: response.data.results, hasMore: response.data.has_more}
      )

    fetchReplies: (search, startTime, page) ->
      params = @_replySearchToParams(search, startTime, page)

      return $http.get('/outgoing/search_replies/?' + $httpParamSerializer(params)).then((response) ->
        utils.parseDates(response.data.results, 'time')
        return {results: response.data.results, hasMore: response.data.has_more}
      )

    startReplyExport: (search) ->
      return $http.post('/replyexport/create/?' + $httpParamSerializer(@_replySearchToParams(search, null, null)))

    #----------------------------------------------------------------------------
    # Convert a regular outbox search object to URL params
    #----------------------------------------------------------------------------
    _outboxSearchToParams: (search, startTime, page) ->
      return {
        folder: search.folder,
        text: search.text,
        contact: if search.contact then search.contact.id else null,
        before: utils.formatIso8601(startTime),
        page: page
      }

    #----------------------------------------------------------------------------
    # Convert a reply search object to URL params
    #----------------------------------------------------------------------------
    _replySearchToParams: (search, startTime, page) ->
      return {
        partner: search.partner.id,
        after: utils.formatIso8601(search.after),
        before: if search.before then utils.formatIso8601(search.before) else utils.formatIso8601(startTime),
        page: page
      }
])


#=====================================================================
# Case service
#=====================================================================
services.factory('CaseService', ['$http', '$httpParamSerializer', '$window', ($http, $httpParamSerializer, $window) ->
  new class CaseService

    #----------------------------------------------------------------------------
    # Fetches old cases
    #----------------------------------------------------------------------------
    fetchOld: (search, before, page) ->
      params = @_searchToParams(search)
      params.before = utils.formatIso8601(before)
      params.page = page

      return $http.get('/case/search/?' + $httpParamSerializer(params)).then((response) ->
        utils.parseDates(response.data.results, 'opened_on')
        return {results: response.data.results, hasMore: response.data.has_more}
      )

    #----------------------------------------------------------------------------
    # Fetches a single case by it's id
    #----------------------------------------------------------------------------
    fetchSingle: (caseId) ->
      return $http.get('/case/fetch/' + caseId + '/').then((response) ->
        caseObj = response.data
        utils.parseDates([caseObj], 'opened_on')
        return caseObj
      )

    #----------------------------------------------------------------------------
    # Starts a case export
    #----------------------------------------------------------------------------
    startExport: (search) ->
      return $http.post('/caseexport/create/?' + $httpParamSerializer(@_searchToParams(search)))

    #----------------------------------------------------------------------------
    # Opens a new case
    #----------------------------------------------------------------------------
    open: (message, summary, assignee) ->
      params = {message: message.id, summary: summary}
      if assignee
        params.assignee = assignee.id

      return $http.post('/case/open/', params).then((response) ->
        caseObj = response.data['case']
        caseObj.isNew = response.data['is_new']
        return caseObj
      )

    #----------------------------------------------------------------------------
    # Adds a note to a case
    #----------------------------------------------------------------------------
    addNote: (caseObj, note) ->
      return $http.post('/case/note/' + caseObj.id + '/', {note: note})

    #----------------------------------------------------------------------------
    # Re-assigns a case
    #----------------------------------------------------------------------------
    reassign: (caseObj, assignee) ->
      return $http.post('/case/reassign/' + caseObj.id + '/', {assignee: assignee.id})
      .then(() ->
        caseObj.assignee = assignee
      )

    #----------------------------------------------------------------------------
    # Closes a case
    #----------------------------------------------------------------------------
    close: (caseObj, note) ->
      return $http.post('/case/close/' + caseObj.id + '/', {note: note})
      .then(() ->
        caseObj.is_closed = true
      )

    #----------------------------------------------------------------------------
    # Re-opens a case
    #----------------------------------------------------------------------------
    reopen: (caseObj, note) ->
      return $http.post('/case/reopen/' + caseObj.id + '/', {note: note})
      .then(() ->
        caseObj.is_closed = false
      )

    #----------------------------------------------------------------------------
    # Re-labels a case
    #----------------------------------------------------------------------------
    relabel: (caseObj, labels) ->
      params = {
        labels: (l.id for l in labels)
      }

      return $http.post('/case/label/' + caseObj.id + '/', params).then(() ->
        caseObj.labels = labels
      )

    #----------------------------------------------------------------------------
    # Updates a case's summary
    #----------------------------------------------------------------------------
    updateSummary: (caseObj, summary) ->
      return $http.post('/case/update_summary/' + caseObj.id + '/', {summary: summary}).then(() ->
        caseObj.summary = summary
      )

    #----------------------------------------------------------------------------
    # Reply in a case
    #----------------------------------------------------------------------------
    replyTo: (caseObj, text) ->
      return $http.post('/case/reply/' + caseObj.id + '/', {text: text})

    #----------------------------------------------------------------------------
    # Fetches timeline events
    #----------------------------------------------------------------------------
    fetchTimeline: (caseObj, after) ->
      params = {after: after}

      return $http.get('/case/timeline/' + caseObj.id + '/?' + $httpParamSerializer(params)).then((response) ->
        for event in response.data.results
          # parse datetime string
          event.time = utils.parseIso8601(event.time)
          event.is_action = event.type == 'A'
          event.is_message_in = event.type == 'M' and event.item.direction == 'I'
          event.is_message_out = event.type == 'M' and event.item.direction == 'O'

        return {results: response.data.results, maxTime: response.data.max_time}
      )

    #----------------------------------------------------------------------------
    # Convert search object to URL params
    #----------------------------------------------------------------------------
    _searchToParams: (search) ->
      return {
        folder: search.folder,
        assignee: if search.assignee then search.assignee.id else null,
        label: if search.label then search.label.id else null
      }
])


#=====================================================================
# Label service
#=====================================================================
services.factory('LabelService', ['$http', ($http) ->
  new class LabelService

    #----------------------------------------------------------------------------
    # Deletes a label
    #----------------------------------------------------------------------------
    delete: (label) ->
      return $http.post('/label/delete/' + label.id + '/')
])


#=====================================================================
# Partner service
#=====================================================================
services.factory('PartnerService', ['$http', ($http) ->
  new class PartnerService

    #----------------------------------------------------------------------------
    # Fetches users with activity statistics for the given partner
    #----------------------------------------------------------------------------
    fetchUsers: (partner) ->
      return $http.get('/partner/users/' + partner.id + '/').then((response) -> response.data.results)

    #----------------------------------------------------------------------------
    # Delete the given partner
    #----------------------------------------------------------------------------
    delete: (partner) ->
      return $http.post('/partner/delete/' + partner.id + '/')
])


#=====================================================================
# User service
#=====================================================================
services.factory('UserService', ['$http', ($http) ->
  new class UserService

    #----------------------------------------------------------------------------
    # Delete the given user
    #----------------------------------------------------------------------------
    delete: (user) ->
      return $http.post('/user/delete/' + user.id + '/')
])


#=====================================================================
# Language service
#=====================================================================
services.factory('LanguageService', ['$http', ($http) ->
  new class LanguageService

    #----------------------------------------------------------------------------
    # Delete the given language
    #----------------------------------------------------------------------------
    delete: (language) ->
      return $http.post('/language/delete/' + language.id + '/')
])


#=====================================================================
# Faq service
#=====================================================================
services.factory('FaqService', ['$http', ($http) ->
  new class FaqService

    #----------------------------------------------------------------------------
    # Delete the given faq
    #----------------------------------------------------------------------------
    delete: (faq) ->
      return $http.post('/faq/delete/' + faq.id + '/')
])


#=====================================================================
# Utils service
#=====================================================================
services.factory('UtilsService', ['$window', '$uibModal', ($window, $uibModal) ->
  new class UtilsService

    displayAlert: (type, message) ->
      $window.displayAlert(type, message)

    navigate: (url) ->
      $window.location.replace(url)

    navigateBack: () ->
      $window.history.back();

    confirmModal: (prompt, style) ->
      resolve = {prompt: (() -> prompt), style: (() -> style)}
      return $uibModal.open({templateUrl: '/partials/modal_confirm.html', controller: 'ConfirmModalController', resolve: resolve}).result

    editModal: (title, initial, maxLength) ->
      resolve = {title: (() -> title), initial: (() -> initial), maxLength: (() -> maxLength)}
      return $uibModal.open({templateUrl: '/partials/modal_edit.html', controller: 'EditModalController', resolve: resolve}).result

    composeModal: (title, initial, maxLength) ->
      resolve = {title: (() -> title), initial: (() -> initial), maxLength: (() -> maxLength)}
      return $uibModal.open({templateUrl: '/partials/modal_compose.html', controller: 'ComposeModalController', resolve: resolve}).result

    assignModal: (title, prompt, partners) ->
      resolve = {title: (() -> title), prompt: (() -> prompt), partners: (() -> partners)}
      return $uibModal.open({templateUrl: '/partials/modal_assign.html', controller: 'AssignModalController', resolve: resolve}).result

    noteModal: (title, prompt, style, maxLength) ->
      resolve = {title: (() -> title), prompt: (() -> prompt), style: (() -> style), maxLength: (() -> maxLength)}
      return $uibModal.open({templateUrl: '/partials/modal_note.html', controller: 'NoteModalController', resolve: resolve}).result

    labelModal: (title, prompt, labels, initial) ->
      resolve = {title: (() -> title), prompt: (() -> prompt), labels: (() -> labels), initial: (() -> initial)}
      return $uibModal.open({templateUrl: '/partials/modal_label.html', controller: 'LabelModalController', resolve: resolve}).result

    newCaseModal: (summaryInitial, summaryMaxLength, partners) ->
      resolve = {summaryInitial: (() -> summaryInitial), summaryMaxLength: (() -> summaryMaxLength), partners: (() -> partners)}
      return $uibModal.open({templateUrl: '/partials/modal_newcase.html', controller: 'NewCaseModalController', resolve: resolve}).result
])
