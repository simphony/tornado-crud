// Tests for the javascript API. 
// IMPORTANT: These tests are not isolated because we rely on an external 
// tornado server which has state. To have them isolated, we would have to
// start and stop the server from javascript at every test, something that 
// is rather hard to achieve from the browser.
define([
    "jsapi/v1/resources"
], function (resources) {
    "use strict";
    
    QUnit.module("Resources");

    QUnit.test("items", function (assert) {
        var done = assert.async();
        resources.Student.items().done(function(item_ids) {
            assert.equal(item_ids.length, 0);
            done();
        });
    });
    
    QUnit.test("create", function (assert) {
        var done = assert.async();
        resources.Student.create(
            {name: "Student", surname: "McStudentface"}
        ).done(function(id) {
            assert.equal(id, "0");
            done();
        });
    });
    
    QUnit.test("items after create", function (assert) {
        var done = assert.async();
        resources.Student.items().done(function(item_ids) {
            assert.equal(item_ids.length, 1);
            assert.equal(item_ids[0], "0");
            done();
        });
    });
    
    QUnit.test("retrieve", function (assert) {
        var done = assert.async();
        resources.Student.retrieve("0").done(function(student) {
            assert.equal(student.name, "Student");
            assert.equal(student.surname, "McStudentface");
            done();
        });
    });
    
    QUnit.test("update", function (assert) {
        var done = assert.async();
        resources.Student.update("0", {name: "Whatever", surname: "McWhateverface"})
            .done(function() {
                resources.Student.retrieve("0").done(
                    function(student) {
                        assert.equal(student.name, "Whatever");
                        assert.equal(student.surname, "McWhateverface");
                        done();
                    }
                );
        });
    });
    
    QUnit.test("update unexistent", function (assert) {
        var done = assert.async();
        resources.Student.update("1", {name: "Whatever", surname: "McWhateverface"})
            .fail(function(error) {
                assert.equal(error.code, 404);
                done();
            });
    });
    
    QUnit.test("retrieve unexistent", function (assert) {
        var done = assert.async();
        resources.Student.retrieve("1").fail(function(error) {
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
