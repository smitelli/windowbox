module.exports = function (grunt) {
    grunt.initConfig({
        pkg : grunt.file.readJSON('package.json'),

        flake8 : {
            options : {
                maxLineLength : 120,
                errorsOnly    : true
            },
            src : ['**/*.py'],
        },

        jshint : {
            options : {
                // Environment
                browser : true,
                node    : true,

                // Enforcing
                camelcase : true,
                curly     : true,
                eqeqeq    : true,
                forin     : true,
                freeze    : true,
                immed     : true,
                indent    : 4,
                latedef   : true,
                maxlen    : 120,
                newcap    : true,
                noarg     : true,
                noempty   : true,
                nonbsp    : true,
                nonew     : true,
                onevar    : true,
                quotmark  : 'single',
                strict    : true,
                trailing  : true,
                undef     : true,
                unused    : true,

                // Relaxing
                loopfunc : true
            },
            src : ['<%= pkg.dir.javascript %>/**/*.js', '!<%= pkg.dir.javascript %>/main-dist.js']
        },

        browserify : {
            dist : {
                files : {
                    '<%= pkg.dir.javascript %>/main-dist.js' : '<%= pkg.dir.javascript %>/main.js'
                }
            }
        },

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
            javascript : {
                files : ['<%= pkg.dir.javascript %>/**/*.js', '!<%= pkg.dir.javascript %>/main-dist.js'],
                tasks : 'browserify'
            },
            stylesheet : {
                files : '<%= pkg.dir.stylesheet %>/**/*.scss',
                tasks : 'sass'
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-sass');
    //grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-browserify');
    grunt.loadNpmTasks('grunt-flake8');

    grunt.registerTask('default', ['watch']);
    grunt.registerTask('lint', ['flake8', 'jshint']);
};
