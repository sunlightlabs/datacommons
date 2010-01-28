
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
            // checkbox
            this.node.find('input.selector').bind('click', function() {
                if (this.checked) {
                    that.select();
                } else {
                    that.deselect();
                }
            });
            // details expander
            this.node.find('a.transactions_control').bind('click', function() {
                var me = $(this);
                var container = that.node.find('.details_container');
                if (me.hasClass('ui-icon-triangle-1-s')) {
                    container.hide();
                } else {    
                    container.show().children('.transactions_container').load(this.href);
                }
                me.trigger('blur').toggleClass('ui-icon-triangle-1-e').toggleClass('ui-icon-triangle-1-s');
                return false;    
            });
            // transaction expander
            this.node.find('.details_expander a').bind('click', function() {
                $(this).trigger('blur');
                that.node.find('.transactions_container').toggleClass('expanded');
                return false;
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
            isError: false,
            isHideable: false,
            interval: null,
            timeout: null,
            
            show: function() {
                $('#statusbar p').text(this.text);
                $('#statusbar').show("slide", { direction: "up" }, 200);
                if (this.isError) {
                    $('#statusbar').addClass('error');
                }
                window.setTimeout(function(msg) {
                    msg.isHideable = true;
                }, 1000, this);
            },
            
            hide: function() {
                this.interval = window.setInterval(function(msg) {
                    if (msg.isHideable) {
                        window.clearInterval(msg.interval);
                        window.clearTimeout(msg.timeout);
                        $('#statusbar').removeClass('error').hide("slide", { direction: "up" }, 200);
                        window.setTimeout(Matchbox.StatusBar.nextMessage, 300);
                    }
                }, 100, this);
            }
            
        },
        
        notify: function(text, isError) {
            var message = Object.create(Matchbox.StatusBar.Message);
            message.text = text;
            message.isError = isError || false;
            Matchbox.StatusBar.queue.push(message);
            if (Matchbox.StatusBar.currentMessage === null) {
                Matchbox.StatusBar.nextMessage();
            }
            return message;
        },
        
        error: function(text) {
            return this.notify(text, true);
        },
        
        nextMessage: function() {
            Matchbox.StatusBar.currentMessage = null;
            var message = Matchbox.StatusBar.queue.shift();
            if (message) {
                Matchbox.StatusBar.currentMessage = message;
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
            $.ajax({
                type: 'GET',
                url: '/search/?type_filter=' + Matchbox.typeFilter + '&q=' + encodeURIComponent(query),
                dataType: 'json',
                success: function(results) {
                    $('#search_terms').append($('<li>' + query + ' (' + results.length + ')</li>'));
                    Matchbox.MergeManager.loadEntities(results);
                },
                error: function(xhr, status, err) {
                    message.hide();
                    message = Matchbox.StatusBar.error('Error loading query: ' + query);
                },
                complete: function() {
                    message.hide();
                }
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
                
                var content = '';
                content += '<li id="' + entity.id + '">';
                content += '<p class="actions">';
                content += '<a href="/entity/' + entity.id + '/" class="transactions" title="transactions">' + entity.count + '</a>';
                content += '<a href="{% url matchbox_google_search %}?q={{ entity.name|urlencode }}" class="google">Google</a>';
                content += '<a href="/entity/' + entity.id + '/" class="detail">Details</a>';
                content += '<a href="/entity/' + entity.id + '/" class="notes" title="notes">' + entity.notes + '</a>';
                content += '</p>';
                content += '<input class="selector" type="checkbox" name="entities" value="' + entity.id + '" id="entities_' + entity.id + '">';
                content += '<a class="transactions_control ui-icon ui-icon-triangle-1-e" href="/entity/' + entity.id + '/transactions/">V</a>';
                content += '<label for="entities_' + entity.id + '">' + entity.name + '</label> <span class="note">$' + entity.total + '</span>';
                content += '<div class="details_container">';
                content += '<div class="transactions_container"></div>';
                content += '<div class="details_expander">';
                content += '<a href="#">=</a>';
                content += '</div>';
                content += '</div>';
                content += '</li>';
                
                var row = $(content);
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
    
    // notes
    $('#note_control').bind('click', function() {
        $(this).hide();
        $('#note_form').show();
        return false;
    });
    $('#note_save').bind('click', function() {
        $.post($('#note_control')[0].href,
            { content: $('#note_form textarea').val() },
            function(response) {
                $('<li class="note"></li>').append(response).prependTo('#notes');
            });
        $('#note_form').hide().children('textarea').val('');
        $('#note_control').show();
        return false;
    });
    $('#note_cancel').bind('click', function() {
        $('#note_form').hide().children('textarea').val('');
        $('#note_control').show();
    });
    
    // edit entity name
    $('#entity_name_container h2').bind('click', function() {
        $('#entity_name_container input[type=text]').val(
            $('#entity_name_container h2').hide().text());
        $('#entity_name_container form').show();
        $('.entity_type').hide();
        return false;
    });
    $('#entity_name_container input[type=submit]').bind('click', function() {
        $.post($('#entity_name_container form')[0].action,
            { name: $('#entity_name_container input[type=text]').val() });
        $('#entity_name_container h2').text(
            $('#entity_name_container input[type=text]').val()).show();
        $('#entity_name_container form').hide();
        $('.entity_type').show();
        return false;
    });
    $('#entity_name_container button').bind('click', function() {
        $('.entity_type').show();
        $('#entity_name_container h2').show();
        $('#entity_name_container form').hide();
        return false;
    });
    
    // attache merge button action
    $('#faux_merge_form').submit(function() {
        if (Matchbox.MergeManager.typeFilter) {
            $('#merge_form').append(
                $('<input type="hidden" name="type_filter" value="' + Matchbox.typeFilter + '">'));
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
    	$('#new_type').val( $('#type_filter').val() );
    	$('#merge_form').trigger('submit');
        return false;
    });
        
});