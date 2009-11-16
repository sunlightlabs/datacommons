
if (typeof Object.create !== 'function') {
    Object.create = function(o) {
        var F = function() {};
        F.prototype = o;
        return new F();
    };
}

var Matchbox = {
    
    Entity: {
        selected: false
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
            $.getJSON('/search/?q=' + encodeURIComponent(query), function(results) {
                Matchbox.MergeManager.loadEntities(results);
                message.hide();
            });
            $('#search_terms').append($('<li>' + query + '</li>'));
            Matchbox.MergeManager.loadedQueries.push(query)
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
                var row = $(entitySpec['html']);
                row.find('input[type=checkbox]').click(function() {
                    Matchbox.MergeManager.entities[$(this).val()].selected = this.checked;
                });
                $('#entities').append(row);
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
    
    // attach select all/none control
    $('#selector').click(function() {
        var checked = $(this).text() == 'All';
        $('#merge_form input[type=checkbox]').each(function() {
            this.checked = checked;
            Matchbox.MergeManager.entities[$(this).val()].selected = checked;
        });
        $(this).trigger('blur').text( $(this).text() == 'All' ? 'None' : 'All' );
        return false;
    });
    
    // attache merge button action
    $('#merge_button').click(function() {
        if (Matchbox.MergeManager.typeFilter) {
            $('#merge_form').append(
                $('<input type="hidden" name="type" value="' + Matchbox.MergeManager.typeFilter + '">'));
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
            me.siblings('.transactions_container').hide();
        } else {    
            me.siblings('.transactions_container').show().load(this.href);
        }
        me.trigger('blur').toggleClass('ui-icon-triangle-1-e').toggleClass('ui-icon-triangle-1-s');
        return false;    
    });
        
});