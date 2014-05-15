module.exports = function (grunt) {
    grunt.initConfig({
        pkg : grunt.file.readJSON('package.json'),

        pkgDir : {
            css : 'windowbox/static/css'
        },

        sass : {
            options : {
                precision    : 5,
                style        : 'compressed',
                unixNewlines : true
            },
            dist : {
                files : {
                    '<%= pkgDir.css %>/main.css' : '<%= pkgDir.css %>/main.scss'
                }
            }
        },

        watch : {
            css : {
                files : '<%= pkgDir.css %>/**/*.scss',
                tasks : ['sass']
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');

    grunt.registerTask('default', ['watch']);
};
