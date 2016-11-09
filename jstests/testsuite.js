(function () {
    require.config({
        baseUrl: "/",
        paths: {
            'jquery' : 'https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min'
        },
        shim: {
          bootstrap: {
            deps: ["jquery"],
            exports: "bootstrap"
          }
        }
    });

	require([
        "tests/test_resources.js",
        ], function() {
            window.apidata = {
                base_url: "/",
                prefix: "/"
            };
            QUnit.load();
            QUnit.start();
	    });
}());


