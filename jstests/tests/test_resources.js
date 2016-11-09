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
});
