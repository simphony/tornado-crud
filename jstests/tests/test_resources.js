// Tests for the javascript API. 
// IMPORTANT: These tests are not isolated because we rely on an external 
// tornado server which has state. To have them isolated, we would have to
// start and stop the server from javascript at every test, something that 
// is rather hard to achieve from the browser.
define([
    "jsapi/v1/resources"
], function (resources) {
    "use strict";
    
    QUnit.config.reorder = false;
    QUnit.module("Resources");

    QUnit.test("interface", function (assert) {
        var done = assert.async();
        resources.Student.items().done(function(items, offset, total) {
            assert.equal(Object.keys(items).length, 0, "no items in the server");
            done();
        });
    });
    
    QUnit.test("create", function (assert) {
        var done = assert.async();
        resources.Student.create(
            {name: "john wick", age: 19}
        ).done(function(id) {
            assert.equal(id, "0", "Create successful");
            done();
        });
    });

    QUnit.test("check length", function (assert) {
        var done = assert.async();
        resources.Student.items().done(
            function(identifiers, items, offset, total) {
                assert.equal(Object.keys(items).length, 1, "item length == 1");
                assert.equal(identifiers.length, 1);
                assert.equal(identifiers[0], "0");
                assert.notEqual(items["0"], undefined);
                done();
            });
        });
    
    QUnit.test("multiple create", function (assert) {
        var done = assert.async(5);
        for (var i = 0; i < 5; i++) {
            resources.Student.create(
                {name: "john wick "+i, age: 19}
            ).done(function(id) {
                assert.ok(id > 0, "New item ids");
                done();
            });
        }
    });

    QUnit.test("checking multiple content", function (assert) {
        var done = assert.async();
        resources.Student.items().done(
            function(identifiers, items, offset, total) {
                assert.equal(Object.keys(items).length, 6, "six elements now present");
                assert.equal(identifiers.length, 6);
                done();
            });
        });

    QUnit.test("items with limit", function (assert) {
        var done = assert.async();
        resources.Student.items({limit: 3}).done(
            function(identifiers, items, offset, total) {
                assert.equal(Object.keys(items).length, 3);
                assert.equal(identifiers.length, 3);
                done();
            });
        });
    
    QUnit.test("items with offset", function (assert) {
        var done = assert.async();
        resources.Student.items({offset: 4, limit: 4}).done(
            function(identifiers, items, offset, total) {
                assert.equal(Object.keys(items).length, 2);
                assert.equal(identifiers.length, 2);
                done();
            });
        });
  
  QUnit.test("items with filter", function (assert) {
    var done = assert.async();
    resources.Student.items({filter: JSON.stringify({"name": "john wick"})}).done(
      function(identifiers, items, offset, total) {
        assert.equal(Object.keys(items).length, 1);
        assert.equal(identifiers.length, 1);
        assert.equal(items[identifiers[0]].name, "john wick");
        done();
      });
  });

    QUnit.test("retrieve", function (assert) {
        var done = assert.async();
        resources.Student.retrieve("0").done(function(student) {
            assert.equal(student.name, "john wick");
            assert.equal(student.age, 19);
            done();
        });
    });
    
    QUnit.test("update", function (assert) {
        var done = assert.async();
        resources.Student.update("0", {name: "Whatever", age: 24})
            .done(function() {
                resources.Student.retrieve("0").done(
                    function(student) {
                        assert.equal(student.name, "Whatever");
                        assert.equal(student.age, 24);
                        done();
                    }
                );
        });
    });
    
    QUnit.test("update unexistent", function (assert) {
        var done = assert.async();
        resources.Student.update("1", {name: "Whatever", age: 19})
            .done(function() {
                assert.notOk();
                done();
            })
            .fail(function(error) {
                assert.equal(error.code, 404);
                done();
            });
    });
    
    QUnit.test("retrieve unexistent", function (assert) {
        var done = assert.async();
        resources.Student.retrieve("1")
            .done(function() {
                assert.notOk();
                done();
            })
            .fail(function(error) {
                assert.equal(error.code, 404);
                done();
            });
    });
    
    QUnit.test("delete", function (assert) {
        var done = assert.async();
        resources.Student.delete("0")
            .done(function() {
                resources.Student.retrieve("0")
                    .fail(function (error) {
                        assert.equal(error.code, 404);
                        done();
                    });
            });
    });
    
    QUnit.test("delete unexistent", function (assert) {
        var done = assert.async();
        resources.Student.delete("0")
            .fail(function (error) {
                assert.equal(error.code, 404);
                done();
            });
    });
  
    QUnit.test("create singleton", function (assert) {
      var done = assert.async();
      resources.ServerInfo.create(
        {uptime: 10, status: "ok"}
      ).done(function(location) {
        assert.equal(location, 
          "http://127.0.0.1:12345/api/v1/serverinfo/", 
          "Create successful");
        done();
      });
    });
  
    QUnit.test("retrieve singleton", function (assert) {
      var done = assert.async();
      resources.ServerInfo.retrieve().done(function(info) {
        assert.equal(info.uptime, 10);
        assert.equal(info.status, "ok");
        done();
      });
    });

    QUnit.test("update", function (assert) {
      var done = assert.async();
      resources.ServerInfo.update({status: "busy", uptime: 20})
        .done(function() {
          resources.ServerInfo.retrieve().done(
            function(info) {
              assert.equal(info.status, "busy");
              assert.equal(info.uptime, 20);
              done();
            }
          );
        });
    });

    QUnit.test("delete", function (assert) {
      var done = assert.async();
      resources.ServerInfo.delete()
        .done(function() {
          resources.ServerInfo.retrieve()
            .fail(function (error) {
              assert.equal(error.code, 404);
              done();
            });
        });
    });
});
