String.prototype.titleize = function() {
    return this.charAt(0).toUpperCase() + this.slice(1);
}

function stringifyDate(date) {
    var year = date.split("-")[0];
    var month = date.split("-")[1];
    var day = date.split("-")[2];
    var months = {
        "01": "January",
        "02": "February",
        "03": "March",
        "04": "April",
        "05": "May",
        "06": "June",
        "07": "July",
        "08": "August",
        "09": "September",
        "10": "October",
        "11": "November",
        "12": "December"
    };

    return months[month] + ' ' + day + ', ' + year;
}

function bioReelSearchClickHandler(that) {
    var bioReel = jQuery(that).parent().parent().parent().parent().parent();
    var bioReelId = bioReel[0].id;
    var thisSearch = jQuery('#' + bioReelId + ' .bioreel-search-input').val();
    var thisContainer = '#' + bioReelId + ' .bioreel-container';    

    if (thisSearch == '') {return}
    // set title
    bioReel.dialog("option", "title", "BioReel - " + thisSearch);    

    // disable search
    jQuery('#' + bioReelId + ' .bioreel-search-button').prop('disabled', true);
    jQuery('#' + bioReelId + ' .bioreel-search-input').prop('disabled', true);

    // set loading graphic
    jQuery(thisContainer).css({'text-align': 'center', 'vertical-align': 'middle'}).html('<img src="/static/loading.gif" />');

    var curDate = '';

    jQuery.get("/v1/query?q=" + thisSearch + '&sort=-timestamp&size=1000', function(data, textStatus, jqXHR) {
        if (data.hits.length == 0) {
            jQuery('#' + bioReelId + ' .bioreel-search-button').prop('disabled', false);
            jQuery('#' + bioReelId + ' .bioreel-search-input').prop('disabled', false);
            jQuery(thisContainer).css({'text-align': 'left', 'vertical-align': 'top'}).html('<p>&nbsp;&nbsp;No results for ' + thisSearch + '</p>');
            
            return
        }
        jQuery('#' + bioReelId + ' .bioreel-link').html('<a href="http://mygene.info/v3/gene/' + thisSearch + '" target="_blank">http://mygene.info/v3/gene/' + thisSearch + '</a>');
        var totalHtml = '<ul class="bioreel-list">';
        jQuery.each(data.hits, function(index, hit) {
            if (hit.timestamp != curDate) {
                var newHtml = (curDate == '') ? ('<li>' + stringifyDate(hit.timestamp) + '<ul class="bioreel-date-list">') : ('</ul></li><li>' + stringifyDate(hit.timestamp) + '<ul class="bioreel-date-list">');
                curDate = hit.timestamp;
                totalHtml += newHtml;
            }
            var newMsg = 'N/A'
            if ('message' in hit.diff.meta) {
                newMsg = hit.diff.meta.message
            }
            else if (hit.diff.op == "update") {
                newMsg = '"' + hit.diff.key + '" key was updated in document';
            }
            else if (hit.diff.op == "add") {
                newMsg = '"' + hit.diff.key + '" key was added to document';
            }
            else if (hit.diff.op == "delete") {
                newMsg = '"' + hit.diff.key + '" key was deleted from document';
            }
            totalHtml += ('<li>' + newMsg + '</li>');
        });
        totalHtml += '</ul></li></ul>';
        jQuery(thisContainer).css({'text-align': 'left', 'vertical-align': 'top'}).html(totalHtml);
        jQuery('#' + bioReelId + ' .bioreel-search-button').prop('disabled', false);
        jQuery('#' + bioReelId + ' .bioreel-search-input').prop('disabled', false);
    });
}

function newBioReel() {
    // creates a new bioreel
    var thisId = 'bioreel-' + jQuery('.bioreel').length;
    jQuery('.bioreel-canvas').append('<div id="' + thisId + '" class="bioreel">' + 
        '<table class="bioreel-table"><tbody><tr class="bioreel-table-header"><td><input class="bioreel-search-input"' +
        ' type="text" placeholder="Search by entrez gene id" /></td><td><button class="bioreel-search-button"><span class="ui-icon ui-icon-search"></span></button>' +
        '</td></tr><tr><td colspan="2" class="bioreel-link"></td></tr><tr><td colspan="2" class="bioreel-container-cell"><div class="bioreel-container"></div></td></tr></tbody></table></div>');
    jQuery('#' + thisId).dialog({'title': 'BioReel - New', 'minWidth': 250, 'height': 400, 'width': 400}).dialogExtend({
        "maximizable": false,
        "dblclick": "minimize",
        "closable": true,
        "minimizable": true,
        "collapsable": false,
        "icons": {
            "minimize": "ui-icon-minusthick",
            "close": "ui-icon-closethick",
            "restore": "ui-icon-plusthick"    
        }
    }).parent().draggable("option", "containment", ".bioreel-canvas").resizable("option", "containment", ".bioreel-canvas").resizable("option", "handles", "e,s,w,se,sw");
    jQuery('#' + thisId + ' .bioreel-search-button').button().click(function() {bioReelSearchClickHandler(this);});
    jQuery('#' + thisId + ' .bioreel-search-input').keyup(function(e) {
        if(e.keyCode == 13) {
            bioReelSearchClickHandler(this)
        }
    });
}

jQuery(document).ready(function() {
    // new Vue for this app
    /*new Vue({
        el: '.bioreel-app'
        // more config
    });*/

    jQuery('#new-bioreel').button().click(newBioReel);
});
