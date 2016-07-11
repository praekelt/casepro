angular.module('cases.controllers')
  .controller('DummyPodController', ['$scope', '$window', '$http', ($scope, $window, $http) ->
    # TODO service for getting case obj
    $scope.caseObj = $window.contextData.case_obj

    # TODO service for this if we use generic view for all plugins
    $http.get('/plugins/dummy')
      .then((d) -> $scope.foo = d.data.foo)
  ])
  .directive('dummyPod', -> {
    templateUrl: '/sitestatic/templates/pods/dummy.html'
  })
