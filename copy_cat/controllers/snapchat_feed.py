from odoo import http, fields
from odoo.http import request
from xml.sax.saxutils import escape


class Feedontroller(http.Controller):

    @http.route('/snapchat-feed.xml', type='http', auth='public')
    def serve_xml_file(self):
        products = request.env['product.template'].search([('allow_snapchat_ads', '=', True)])
        base_url = request.httprequest.host_url.rstrip('/')

        xml_content = """<?xml version="1.0" encoding="utf-8"?>
        <rss version="2.0" xmlns:g="http://base.google.com/ns/1.0" xmlns:atom="http://www.w3.org/2005/Atom">
            <channel> 
                <title>BabyLife</title>
                <description>Product Feed for Facebook</description> 
                <link>{}</link>
                <lastBuildDate>{}</lastBuildDate>
        """.format(base_url, fields.Datetime.now())

        for product in products:
            brand_name = product.feed_brand_id.name if product.feed_brand_id else ''
            if product.google_category_id:
                if isinstance(product.google_category_id, str):
                    google_category_name = product.google_category_id
                else:
                    google_category_name = product.google_category_id.name.replace('&', '&amp;')
            else:
                google_category_name = ''

            # Iterate over each product variant
            for product_variant in product.product_variant_ids:
                image_url = "{}/web/image/product.product/{}/image_1920".format(base_url, product_variant.id)
                # Include the product attribute in the product URL
                product_url = "{}{}".format(base_url, product_variant.website_url)
                product_name = escape(product_variant.name)
                product_description = escape(product_variant.description or '')

                # Get attributes of the product variant
                variant_attributes = {}
                for attribute_value in product_variant.product_template_attribute_value_ids:
                    attribute_name = attribute_value.attribute_id.name
                    attribute_value_name = attribute_value.name
                    variant_attributes[attribute_name] = attribute_value_name

                # Construct the attribute string
                attribute_string = ','.join([f"{name}:{value}" for name, value in variant_attributes.items()])

                xml_content += """
                <item>
                    <g:id>{}</g:id>
                    <g:title>{}</g:title>
                    <g:description><![CDATA[{}]]></g:description>
                    <g:link>{}</g:link>
                    <g:image_link>{}</g:image_link>
                    <g:availability>in_stock</g:availability>
                    <g:price>{}</g:price>
                    <g:sale_price/>
                    <g:sale_price_effective_date/>
                    <g:google_product_category>{}</g:google_product_category>
                    <g:brand>{}</g:brand>
                    <g:gtin>{}</g:gtin>
                    <g:mpn>{}</g:mpn>
                    <g:condition>new</g:condition>
                    <g:item_group_id>{}</g:item_group_id>
                    <g:additional_image_link>{}</g:additional_image_link>
                </item>
                """.format(
                    product_variant.id,
                    product_name,
                    product_description,
                    product_url,
                    image_url,
                    product_variant.list_price,
                    google_category_name,
                    brand_name,
                    product_variant.barcode,
                    product_variant.default_code,
                    product_variant.id,
                    attribute_string
                )

        xml_content += """
            </channel>
        </rss>
        """

        headers = [
            ('Content-Type', 'application/xml'),
            ('Content-Disposition', 'inline'),
        ]

        return request.make_response(xml_content, headers=headers)
