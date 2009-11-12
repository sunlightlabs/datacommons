
var Matchbox = {
        
    Entity: function(spec) {
        if (spec) {
            this.id = spec['id'];
            this.type = spec['type'];
            this.name = spec['name'];
            this.count = spec['count'] ? spec['count'] : 0;
            this.notes = spec['notes'] ? spec['notes'] : 0;
            this.aliases = spec['aliases'] ? spec['aliases'] : [];
        }
        this.selected = false;
    },
    
    MergeManager: {
        
        entities: { },
        loadedQueries: [],
        loadedQueues: [],
        typeFilter: null,
        
        StatusBar: {
            shouldHide: false,
            show: function(message) {
                $('#statusbar p').text(message).parent().show("slide", { direction: "up" }, 500);
                var interval = window.setInterval(function () {
                    if (Matchbox.MergeManager.StatusBar.shouldHide) {
                        Matchbox.MergeManager.StatusBar.shouldHide = false;
                        clearInterval(interval);
                        $('#statusbar').hide("slide", { direction: "up" }, 1000);
                    }
                }, 800);
            },
            hide: function() {
                Matchbox.MergeManager.StatusBar.shouldHide = true;
            }
        },
        
        loadEntities: function(entities) {
            for (var i = 0; i < entities.length; i++) {
                Matchbox.MergeManager.register(entities[i]);
            }
            Matchbox.MergeManager.StatusBar.hide();
        },
        
        loadQuery: function(query) {
            Matchbox.MergeManager.StatusBar.show("Loading query '" + query + "'");
            $.getJSON('/search/?q=' + encodeURIComponent(query), Matchbox.MergeManager.loadEntities);
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
                var entity = new Matchbox.Entity(entitySpec)
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