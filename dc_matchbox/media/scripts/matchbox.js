
if (typeof Object.create !== 'function') {
    Object.create = function(o) {
        var F = function() {};
        F.prototype = o;
        return new F();
    };
}

var Matchbox = {
    
    typeFilter: null,
    searchQueries: [],
    queueId: null,
    
    entities: [],
    
    Entity: {
        
        id: null,
        selected: false,
        node: null,
        
        select: function() {
            this.selected = true;
            if (this.node) {
                this.node.find('input.selector').each(function() {
                    this.checked = true;
                });
            }
        },
        
        deselect: function() {
            this.selected = false;
            if (this.node) {
                this.node.find('input.selector').each(function() {
                    this.checked = false;
                });
            }
        },
        
        bind: function() {
            var that = this;
            this.node = $('#' + this.id);
            this.node.find('input.selector').bind('click', function() {
                if (this.checked) {
                    that.select();
                } else {
                    that.deselect();
                }
            });
        }
        
    },    
        
    toggleEntities: function(checked) {
        for (var i = 0; i < Matchbox.entities.length; i++) {
            if (checked) {
                Matchbox.entities[i].select();
            } else {
                Matchbox.entities[i].deselect();
            }
        }
    },
    
    selectedEntities: function() {
        var entities = [];
        for (var i = 0; i < Matchbox.entities.length; i++) {
            if (Matchbox.entities[i].selected) {
                entities.push(Matchbox.entities[i]);
            }
        }
        return entities;
    },
    
    createEntity: function(spec) {
        if (spec) {
            var e = Object.create(Matchbox.Entity);
            e.id = spec.id;
            e.type = spec.type;
            e.name = spec.name;
            e.count = spec.count || 0;
            e.notes = spec.notes || 0;
            e.aliases = spec.aliases || [];
            return e;
        }
    },    
        
    StatusBar: {
        
        queue: [],
        currentMessage: null,
        
        Message: {
            
            text: '',
            isHideable: false,
            interval: null,
            timeout: null,
            
            show: function() {
                $('#statusbar p').text(this.text).parent().show("slide", { direction: "up" }, 500);
                window.setTimeout(function(msg) {
                    msg.isHideable = true;
                }, 1500, this);
            },
            
            hide: function() {
                this.interval = window.setInterval(function(msg) {
                    if (msg.isHideable) {
                        window.clearInterval(msg.interval);
                        window.clearTimeout(msg.timeout);
                        $('#statusbar').hide("slide", { direction: "up" }, 500);
                        window.setTimeout(Matchbox.StatusBar.nextMessage, 600);
                    }
                }, 100, this);
            }
            
        },
        
        notify: function(text) {
            var message = Object.create(Matchbox.StatusBar.Message);
            message.text = text;
            Matchbox.StatusBar.queue.push(message);
            if (!Matchbox.StatusBar.currentMessage) {
                Matchbox.StatusBar.nextMessage();
            }
            return message;
        },
        
        nextMessage: function() {
            var message = Matchbox.StatusBar.queue.shift();
            this.currentMessage = message;
            if (message) {
                message.show();
            }
        }
        
    },
    
    MergeManager: {
        
        entities: { },
        loadedQueries: [],
        loadedQueues: [],
        typeFilter: null,
        
        loadEntities: function(entities) {
            for (var i = 0; i < entities.length; i++) {
                Matchbox.MergeManager.register(entities[i]);
            }
        },
        
        loadQuery: function(query) {
            var message = Matchbox.StatusBar.notify("Loading query '" + query + "'");
            $.getJSON('/search/?type=' + Matchbox.typeFilter + '&q=' + encodeURIComponent(query), function(results) {
                $('#search_terms').append($('<li>' + query + ' (' + results.length + ')</li>'));
                Matchbox.MergeManager.loadEntities(results);
                message.hide();
            });
            Matchbox.MergeManager.loadedQueries.push(query)
            Matchbox.searchQueries.push(query)
        },
        
        loadQueue: function(queueId) {
            $.getJSON('/queue/' + queueId + '/', Matchbox.MergeManager.loadEntities);
            Matchbox.MergeManager.loadedQueues.push(queueId)
            //$('<input type="hidden" name="queue" value="' + queueId + '">').appendTo('#merge_form')
        },
        
        register: function(entitySpec) {
            if (entitySpec['id'] in Matchbox.MergeManager.entities) {
                // duplicate, ignore
            } else {
                var entity = Matchbox.createEntity(entitySpec);
                Matchbox.MergeManager.entities[entity['id']] = entity;
                Matchbox.entities.push(entity);
                var row = $(entitySpec['html']);
                // row.find('input[type=checkbox]').click(function() {
                //     Matchbox.MergeManager.entities[$(this).val()].selected = this.checked;
                // });
                $('#entities').append(row);
                entity.bind();
            }
        },
        
        selectedEntities: function() {
            var entities = [];
            for (id in Matchbox.MergeManager.entities) {
                var entity = Matchbox.MergeManager.entities[id];
                if (entity.selected) {
                    entities.push(entity);
                }
            }
            return entities;
        }
        
    }
    
}

/* 
 * on page load
 */

$().ready(function() {
    
    $('#test').bind('click', function() {
        alert(Matchbox.typeFilter, {
            minChars: 0,
            scroll: true,
            scrollHeight: 50,
            width: 200
        });
        return false;
    });
    
    $('#merge_name').bind('focus', function() {
        var names = [];
        var entities = Matchbox.selectedEntities();
        for (var i = 0; i < entities.length; i++) {
            names.push(entities[i].name);
        }
        $(this).autocomplete(names);
    });
    
    // $().bind('ajaxError', function(e, xhr, ajaxOptions, thrownError) {
    //     Matchbox.StatusBar.notify(xhr.statusText);
    //     if (Matchbox.StatusBar.currentMessage) {
    //         Matchbox.StatusBar.currentMessage.hide();
    //     }
    // });
    
    // attach search form validation    
    $('#search_form').submit(function() {
        if ($('#query').val().trim() == '') {
            alert('please enter a search term');
            return false;
        }
    });
    
    // more results search form
    $('#more_results_form').submit(function() {
        var query = $('#more_results_query').val().trim();
        if (query == '') {
            alert('please enter a search term');
        } else {
            Matchbox.MergeManager.loadQuery(query);
            $('#more_results_query').val('');
        }
        return false;
    });
    
    // select all/none toggles
    $('#selectAll').bind('click', function() {
        Matchbox.toggleEntities(true);
        return false;
    });
    $('#selectNone').bind('click', function() {
        Matchbox.toggleEntities(false);
        return false;
    });
    
    // attache merge button action
    $('#merge_button').click(function() {
        if (Matchbox.MergeManager.typeFilter) {
            $('#merge_form').append(
                $('<input type="hidden" name="type" value="' + Matchbox.typeFilter + '">'));
        }
        for (var i = 0; i < Matchbox.MergeManager.loadedQueries.length; i++) {
            var query = Matchbox.MergeManager.loadedQueries[i];
            $('#merge_form').append($('<input type="hidden" name="query" value="' + query + '">'))
        }
        for (var i = 0; i < Matchbox.MergeManager.loadedQueues.length; i++) {
            var queueId = Matchbox.MergeManager.loadedQueues[i];
            $('#merge_form').append($('<input type="hidden" name="queue" value="' + queueId + '">'))
        }
    	$('#new_name').val( $('#merge_name').val() );
    	$('#new_type').val( $('#merge_type').val() );
        $('#merge_form').trigger('submit');
        return false;
    });
    
    // transactions control
    $('a.transactions_control').live('click', function() {
        var me = $(this);
        if (me.hasClass('ui-icon-triangle-1-s')) {
            me.siblings('.details_container').hide();
        } else {    
            me.siblings('.details_container').show().children('.transactions_container').load(this.href);
        }
        me.trigger('blur').toggleClass('ui-icon-triangle-1-e').toggleClass('ui-icon-triangle-1-s');
        return false;    
    });
    $('.details_expander a').live('click', function() {
        $(this).trigger('blur').parent().siblings('.transactions_container').toggleClass('expanded');
        return false;
    });
        
});