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
        resources.Student.items().done(function(item_ids) {
            assert.equal(item_ids.length, 0, "no items in the server");
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
        resources.Student.items().done(function(item_ids) {
            assert.equal(item_ids.length, 1, "item length == 1");
            assert.equal(item_ids[0], "0", "one item present");
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
        resources.Student.items().done(function(item_ids) {
            assert.equal(item_ids.length, 6, "six elements now present");
            done();
        });
    });

    QUnit.test("items with limit", function (assert) {
        var done = assert.async();
        resources.Student.items({limit: 3}).done(function(item_ids) {
            assert.equal(item_ids.length, 3);
            done();
        });
    });
    
    QUnit.test("items with offset", function (assert) {
        var done = assert.async();
        resources.Student.items({offset: 4, limit: 4}).done(function(item_ids) {
            assert.equal(item_ids.length, 2);
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
});
