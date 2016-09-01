filters = angular.module('cases.filters', []);


#----------------------------------------------------------------------------
# Formats a date value in same style as GMail
#----------------------------------------------------------------------------
filters.filter('autodate', (dateFilter) ->
  return (date) ->
    now = new Date()
    isToday = date.getDate() == now.getDate() and date.getMonth() == now.getMonth() and date.getFullYear() == now.getFullYear()

    if isToday
      return dateFilter(date, 'HH:mm')
    else if date.getFullYear() == now.getFullYear()
      return dateFilter(date, 'MMM d')
    else
      return dateFilter(date, 'MMM d, yyyy')
)
#----------------------------------------------------------------------------
# Formats a date value as a full timestamp
#----------------------------------------------------------------------------
filters.filter('fulldate', (dateFilter) ->
  return (date) ->
    return dateFilter(date, 'MMM d, yyyy HH:mm')
)

#----------------------------------------------------------------------------
# Reverses an array of items
#----------------------------------------------------------------------------
filters.filter('reverse', () ->
  return (items) ->
    return items.slice().reverse()
)

#----------------------------------------------------------------------------
# Encodes URL components
#----------------------------------------------------------------------------
filters.filter('urlencode', ['$window', ($window) ->
  return (input) ->
    return $window.encodeURIComponent(input)
])


#----------------------------------------------------------------------------
# Replaces underscores with spaces
#----------------------------------------------------------------------------
filters.filter('deunderscore', () ->
    return (input) ->
        return input.replace(/_/g, ' ')
)
