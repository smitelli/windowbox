module.exports = function (grunt) {
    grunt.initConfig({
        pkg : grunt.file.readJSON('package.json'),

        sass : {
            options : {
                precision    : 5,
                style        : 'compressed',
                unixNewlines : true
            },
            dist : {
                files : {
                    '<%= pkg.dir.stylesheet %>/main.css' : '<%= pkg.dir.stylesheet %>/main.scss'
                }
            }
        },

        watch : {
            stylesheet : {
                files : '<%= pkg.dir.stylesheet %>/**/*.scss',
                tasks : 'sass'
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');

    grunt.registerTask('default', ['watch']);
};
