define(['jquery'], function ($) {
    "use strict";
    
    var url_path_join = function () {
        // join a sequence of url components with '/'
        var url = '', i = 0;

        for (i = 0; i < arguments.length; i += 1) {
            if (arguments[i] === '') {
                continue;
            }
            if (url.length > 0 && url[url.length-1] !== '/') {
                url = url + '/' + arguments[i];
            } else {
                url = url + arguments[i];
            }
        }
        url = url.replace(/\/\/+/, '/');
        return url;
    };
    
    var update = function (d1, d2) {
        // Transfers the keys from d2 to d1. Returns d1
        $.map(d2, function (i, key) {
            d1[key] = d2[key];
        });
        return d1;
    };
    
    var encode_uri_components = function (uri) {
        // encode just the components of a multi-segment uri,
        // leaving '/' separators
        return uri.split('/').map(encodeURIComponent).join('/');
    };

    var API = (function () {
        // Object representing the interface to the Web API.
        // @param base_url : the url at which to find the web API endpoint.
        var self = this;
        this.base_urlpath = "{{ base_urlpath }}";

        this.default_options = {
            contentType: "application/json",
            cache: false,
            dataType : null,
            processData: false,
            success: null,
            error: null
        };
        
        this.request = function (req_type, endpoint, body, success_cb, fail_cb) {
            // Performs a request to the final endpoint
            var options = {};
            update(options, self.default_options);
            update(options, {
                type: req_type,
                body: body,
                success: success_cb,
                fail: fail_cb
            });
            
            var url = url_path_join(
                    self.base_urlpath, 
                    "api", "{{ api_version }}",
                    encode_uri_components(endpoint)
                )+'/';

            return $.ajax(url, options);
        };
    })();

    var Resource = function(type) {
        this.type = type;
        
        this.create = function(representation, success_cb, fail_cb) {
            API.request("POST", type, representation, success_cb, fail_cb);
        };

        this.delete = function(id, success_cb, fail_cb) {
            API.request("DELETE", url_path_join(type, id), success_cb, fail_cb);
        };

        this.retrieve = function(id, success_cb, fail_cb) {
            API.request("GET", url_path_join(type, id), success_cb, fail_cb);
        };

        this.items = function(success_cb, fail_cb) {
            API.request("GET", type, success_cb, fail_cb);
        };
    };

    return {
        {% for res in resources %}"{{ res['class_name'] }}" : new Resource("{{ res['collection_name'] }}"),
        {% end %} };
});

