(function() {
    var console = parent.console;
    
    // Define all of the boilerplate classes, which only really matter the first time the code gets loaded
    var PgParser = function() {
        this.threads = {};
    }
    
    PgParser.prototype.loadPage = function() {
        var hash = parent.location.hash;
        if (this.threads[hash] === undefined) {
            this.threads[hash] = {};
        }
        
        var parser = this;
        $(document).find('.Bk').each(function(index, message) {
            var body = $(message).find('.ii.gt>div');
            
            if (parser.threads[hash][index] === undefined) {
                parser.threads[hash][index] = new PgMessage(hash, index);
            }
            
            if (body.length > 0 && !body.eq(0).hasClass('pg-rendered')) {
                parser.threads[hash][index].renderIfAvailable();
            }
        })
    }
    
    PgParser.prototype.fetchData = function() {
        var hash = parent.location.hash;
        var parser = this;
        $.each(parser.threads[hash], function(index, message) {
            message.fetchAndRender();
        });
    }
    
    var PgMessage = function(hash, index) {
        this.state = 'not fetched';
        this.hash = hash;
        this.index = index;
    }
    
    PgMessage.prototype.getDiv = function() {
        return $(document).find('.Bk').eq(this.index).find('.ii.gt>div');
    }
    
    PgMessage.prototype.fetch = function(callback) {
        if (this.state == 'fetched') {
            callback();
            return;
        }
        
        var div = this.getDiv();
        if (div.length == 0) return;
        var text = div.html();
        var origMessage = this;
        this.state = 'fetching';
        
        //Submit to Poligraft
        $.getJSON('http://poligraft.com/poligraft?json=1&text=' + encodeURIComponent(text) + '&callback=?',
            function(data) {
                var endpoint = 'http://poligraft.com/' + data.slug + '.json?callback=?'
                var interval = setInterval(function() {
                    $.getJSON(endpoint, function(realData) {
                        if (realData.processed) {
                            origMessage.pgData = realData;
                            origMessage.state = 'fetched';
                            console.log(realData);
                            clearInterval(interval);
                            callback();
                        }
                    })
                }, 2000);
            }
        );        
    }
    
    PgMessage.prototype.renderIfAvailable = function() {
        if (this.hash == parent.location.hash) {
            var div = this.getDiv();
            if (this.state == 'fetched' && !div.hasClass('pg-rendered') && div.length > 0) {
                div.removeClass('pg-fetching');
                div.addClass('pg-rendered');
                
                var text = div.html();
                $.each(this.pgData.entities, function(num, entity) {
                    if (!entity.tdata_id) return;
                    var label = "<span class='pg-wrapper'><div class='pg-insert'>"
                        + "<h3>" + entity.tdata_name +"</h3>"
                        + (entity.recipient_breakdown.dem === undefined ? "" : "Demsocrats: " + entity.recipient_breakdown.dem + "%; Republicans: " + entity.recipient_breakdown.rep + "%")
                        + (entity.contributor_breakdown.individual === undefined ? "" : "Individual: " + entity.contributor_breakdown.individual + "%; Republicans: " + entity.contributor_breakdown.pac + "%")
                        + "</div><span class='pg-highlighted'>" + entity.name + "</span></span>";
                    text = text.replace(entity.name, label);
                })
                div.html(text);
                
                div.find('.pg-wrapper').hover(function() {
                    $(this).find('.pg-insert').show();
                }, function() {
                    $(this).find('.pg-insert').hide();
                })
            } else if (this.state == 'fetching' && !div.hasClass('pg-fetching') && div.length > 0) {
                div.addClass('pg-fetching');
            }
        }
    }
    
    PgMessage.prototype.fetchAndRender = function() {
        var origMessage = this;
        this.fetch(function(div) {
            origMessage.renderIfAvailable();
        });
        origMessage.renderIfAvailable();
    }
    
    
    // Check to see if the Poligraft class has already been loaded and, if not, load it
    if (window.poligraftParser === undefined) {
        window.poligraftParser = new PgParser();
    }
    
    // Check to see whether or not the stylesheet as been loaded, and, if not, load it.
    var sheets = $(document.documentElement).find('head').find('link[rel=stylesheet]').map(function() { return $(this).attr('href'); });
    var stylesLoaded = false;
    $.each(sheets, function(index, sheet) {
        if (sheet.indexOf('poligraft-rapportive.css') != -1) {
            stylesLoaded = true;
        }
    })
    if (!stylesLoaded) {
        console.log('loading the sheet');
        $(document.documentElement).find('head').append('<link rel="stylesheet" type="text/css" href="{{ host }}/media/css/poligraft-rapportive.css" />')
    }
    
    // Reparse the current page and enable the button
    window.poligraftParser.loadPage();
    $(document).find('#poligraft-rapportive input').click(function() {
        window.poligraftParser.fetchData();
    }).removeAttr('disabled');
})();