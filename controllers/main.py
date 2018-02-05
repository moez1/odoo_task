# -*- coding: utf-8 -*-

from odoo.addons.website_sale.controllers.main import *
from odoo import http
from odoo.http import request
import json
import urllib2


class WebsiteSale(WebsiteSale):

    def get_place_id(self, adress, api_key):
        # get the place_id for the specifc adress using google maps api
        res = False

        url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query=' + adress + '&key='+ api_key +''
        result = json.load(urllib2.urlopen(url))
        res = result['results'][0].get('place_id')
        return res

    def checkout_form_validate(self, mode, all_form_values, data):
        # we override this funtion to validate the phone number and zip code field

        error, error_message = super(WebsiteSale, self).checkout_form_validate(mode, all_form_values, data)
        api_key = request.env['website.config.settings'].browse(1).google_maps_api_key
        country_name = False

        if data["country_id"]:
            country_name = request.env['res.country'].browse(int(data["country_id"])).name
        adress = data["street"] + " " + data["city"] + " " + country_name
        format_adress = '+'.join(adress.split())
        place_id = self.get_place_id(format_adress, api_key)

        if place_id:
            url = 'https://maps.googleapis.com/maps/api/place/details/json?placeid=' + place_id + '&key=' + api_key + ''
            result = json.load(urllib2.urlopen(url))

            for res in result['result']['address_components']:
                if res['types'][0] == "postal_code":
                    if res['short_name'] != data["zip"]:
                        error["zip"] = 'error'
                        error_message.append('Invalid Zip Code! Please enter a valid Zip Code.')
            if result['result'].get('formatted_phone_number') and result['result'].get('formatted_phone_number') != data["phone"]:
                error["phone"] = 'error'
                error_message.append('Invalid Phone Number! Please enter a valid Phone Number.')
        else:
            error["street"] = 'error'
            error_message.append('Invalid Adress! Please enter a valid Adress.')
        return error, error_message
    
    