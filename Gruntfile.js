module.exports = function(grunt) {
    "use strict";
    grunt.initConfig({
        copy: {
            jquery: {
                nonull: true,
                src: 'bower_components/jquery/dist/jquery.js',
                dest: 'src/js/jquery.js'
            },
            bootstrap_less: {
                expand: true,
                cwd: 'bower_components/bootstrap/less/',
                src: '**',
                dest: 'src/less/bootstrap/'
            },
            bootstrap_js: {
                expand: true,
                cwd: 'bower_components/bootstrap/js/',
                src: '**',
                dest: 'src/js/bootstrap'
            }
        },
        concat: {
            plugins: {
                src: [
                    'bower_components/jquery-file-upload/js/vendor/jquery.ui.widget.js',
                    'bower_components/jquery-file-upload/js/jquery.iframe-transport.js',
                    'bower_components/jquery-file-upload/js/jquery.fileupload.js'
                ],
                dest: 'static/js/plugins.js'
            },
            bootstrap: {
                src: [
                    'src/js/bootstrap/transition.js',
                    'src/js/bootstrap/alert.js',
                    'src/js/bootstrap/button.js',
                    'src/js/bootstrap/carousel.js',
                    'src/js/bootstrap/collapse.js',
                    'src/js/bootstrap/dropdown.js',
                    'src/js/bootstrap/modal.js',
                    'src/js/bootstrap/tooltip.js',
                    'src/js/bootstrap/popover.js',
                    'src/js/bootstrap/scrollspy.js',
                    'src/js/bootstrap/tab.js',
                    'src/js/bootstrap/affix.js'
                ],
                dest: 'static/js/main.js'
            }
        },
        less: {
            build: {
                options: {
                    compress: false,
                    yuicompress: true,
                    optimization: 2
                },
                files: {
                    // target.css file: source.less file
                    'static/css/main.css': 'src/less/_main.less'
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-copy');

    grunt.registerTask('default', ['copy', 'concat', 'less']);
};