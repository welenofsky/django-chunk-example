module.exports = function(grunt) {
    "use strict";
    grunt.initConfig({
        concat: {
            jquery: {
                src: 'bower_components/jquery/dist/jquery.js',
                dest: 'static/js/jquery.js'
            },
            plugins: {
                src: [
                    'bower_components/jquery-file-upload/js/vendor/jquery.ui.widget.js',
                    'bower_components/jquery-file-upload/js/jquery.iframe-transport.js',
                    'bower_components/jquery-file-upload/js/jquery.fileupload.js'
                ],
                dest: 'static/js/plugins.js'
            }
        }
    });

    //grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-concat');

    grunt.registerTask('default', ['concat']);
};