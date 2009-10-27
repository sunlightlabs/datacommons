
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
        
        loadEntities: function(entities) {
            for (var i = 0; i < entities.length; i++) {
                Matchbox.MergeManager.register(entities[i]);
            }
        },
        
        loadQuery: function(query) {
            $.getJSON('/search/?q=' + query, Matchbox.MergeManager.loadEntities);
        },
        
        loadQueue: function(queueId) {
            $.getJSON('/queue/' + queueId + '/', Matchbox.MergeManager.loadEntities);
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
                $('#entities_table').append(row);
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
    	$('#name').val( $('#merge_name').val() );
    	$('#type').val( $('#merge_type').val() );
        $('#merge_form').trigger('submit');
        return false;
    });
    
    $('#more_results_form').submit(function() {
        var query = $('#more_results_query').val().trim();
        if (query == '') {
            alert('please enter a search term');
        } else {
            Matchbox.MergeManager.loadQuery(query);
        }
        return false;
    });
        
});