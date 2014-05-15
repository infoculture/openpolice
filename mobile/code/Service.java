
package ru.mvd.service;

import android.util.Log;
import com.github.kevinsawicki.http.HttpRequest;
import java.io.IOException;
import java.io.InputStream;
import java.io.UnsupportedEncodingException;
import java.net.URLEncoder;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Set;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.mime.MultipartEntity;
import org.apache.http.impl.client.DefaultHttpClient;
import org.json.JSONException;
import ru.mvd.models.Request;

// Referenced classes of package ru.mvd.service:
//            SimpleItemResponse, DepartmentResponse, EmergencyResponse, LocationResponse, 
//            NewsResponse, PageResponse, PoliceOfficerResponse, SynchronizeResponse, 
//            SynchronizeLastResponse, SynchronizeRazdelResponse, WantedItemResponse, WantedThemeResponse, 
//            ServiceHelper, Response, IResponse

public class Service
{

    private static final String servicePath = "http://mvd.ru/api/";

    public Service()
    {
    }

    private static String customRequest(String s)
    {
        Log.d("myLogs", s);
        HttpRequest httprequest = HttpRequest.get(s);
        httprequest.userAgent("Android");
        String s1;
        try
        {
            s1 = httprequest.body();
        }
        catch (Exception exception)
        {
            return "";
        }
        return s1;
    }

    public static SimpleItemResponse getAddressCity(String s)
    {
        HashMap hashmap = new HashMap();
        hashmap.put("parent", s);
        return new SimpleItemResponse(request("address/city", hashmap));
    }

    public static SimpleItemResponse getAddressCityZone(String s)
    {
        HashMap hashmap = new HashMap();
        hashmap.put("parent", s);
        return new SimpleItemResponse(request("address/city_zone", hashmap));
    }

    public static SimpleItemResponse getAddressHouseDistrict(String s, String s1, String s2, String s3)
    {
        HashMap hashmap = new HashMap();
        hashmap.put("subject", String.valueOf(s));
        hashmap.put("subzone", String.valueOf(s1));
        hashmap.put("city", String.valueOf(s2));
        hashmap.put("street", String.valueOf(s3));
        hashmap.put("search", "district");
        return new SimpleItemResponse(request("address/house", hashmap));
    }

    public static SimpleItemResponse getAddressHouseDivision(String s, String s1, String s2, String s3)
    {
        HashMap hashmap = new HashMap();
        hashmap.put("subject", String.valueOf(s));
        hashmap.put("subzone", String.valueOf(s1));
        hashmap.put("city", String.valueOf(s2));
        hashmap.put("street", String.valueOf(s3));
        hashmap.put("search", "division");
        return new SimpleItemResponse(request("address/house", hashmap));
    }

    public static SimpleItemResponse getAddressMunicipality(String s)
    {
        HashMap hashmap = new HashMap();
        hashmap.put("parent", s);
        return new SimpleItemResponse(request("address/subzone", hashmap));
    }

    public static SimpleItemResponse getAddressRegion()
    {
        return new SimpleItemResponse(request("address/subject"));
    }

    public static SimpleItemResponse getAddressStreet(String s)
    {
        HashMap hashmap = new HashMap();
        hashmap.put("parent", s);
        return new SimpleItemResponse(request("address/street", hashmap));
    }

    public static DepartmentResponse getDepartments(double d, double d1, int i)
    {
        HashMap hashmap = new HashMap();
        hashmap.put("lat", String.valueOf(d));
        hashmap.put("lng", String.valueOf(d1));
        hashmap.put("accuracy", String.valueOf(i));
        return new DepartmentResponse(request("division", hashmap));
    }

    public static EmergencyResponse getEmergency(double d, double d1, int i)
    {
        HashMap hashmap = new HashMap();
        hashmap.put("lat", String.valueOf(d));
        hashmap.put("lng", String.valueOf(d1));
        hashmap.put("accuracy", String.valueOf(i));
        return new EmergencyResponse(request("emergency", hashmap));
    }

    public static LocationResponse getLocation()
    {
        return new LocationResponse(request("location"));
    }

    public static LocationResponse getLocation(double d, double d1)
    {
        HashMap hashmap = new HashMap();
        hashmap.put("lat", String.valueOf(d));
        hashmap.put("lng", String.valueOf(d1));
        return new LocationResponse(request("location", hashmap));
    }

    public static NewsResponse getNews(int i, int j)
    {
        HashMap hashmap = new HashMap();
        hashmap.put("limit", String.valueOf(i));
        hashmap.put("offset", String.valueOf(j));
        return new NewsResponse(request("news", hashmap));
    }

    public static PageResponse getPages(int i, int j)
    {
        HashMap hashmap = new HashMap();
        hashmap.put("type", String.valueOf(i));
        if (j != 0)
        {
            hashmap.put("parent_id", String.valueOf(j));
        }
        return new PageResponse(request("pages", hashmap));
    }

    private static String getParamStr(HashMap hashmap)
    {
        String s = "";
        if (hashmap == null) goto _L2; else goto _L1
_L1:
        Iterator iterator = hashmap.keySet().iterator();
_L3:
        String s1;
        if (!iterator.hasNext())
        {
            break; /* Loop/switch isn't completed */
        }
        s1 = (String)iterator.next();
        String s2 = (new StringBuilder()).append(s).append("&").append(s1).append("=").append(URLEncoder.encode((String)hashmap.get(s1), "UTF-8")).toString();
        s = s2;
        continue; /* Loop/switch isn't completed */
        UnsupportedEncodingException unsupportedencodingexception;
        unsupportedencodingexception;
        unsupportedencodingexception.printStackTrace();
        if (true) goto _L3; else goto _L2
_L2:
        return s;
    }

    public static PoliceOfficerResponse getPoliceOfficers(double d, double d1, int i)
    {
        HashMap hashmap = new HashMap();
        hashmap.put("lat", String.valueOf(d));
        hashmap.put("lng", String.valueOf(d1));
        hashmap.put("accuracy", String.valueOf(i));
        return new PoliceOfficerResponse(request("district", hashmap));
    }

    public static NewsResponse getRegionNews(int i, int j, int k)
    {
        HashMap hashmap = new HashMap();
        hashmap.put("limit", String.valueOf(i));
        hashmap.put("offset", String.valueOf(j));
        hashmap.put("region", String.valueOf(k));
        return new NewsResponse(request("news/region", hashmap));
    }

    public static SynchronizeResponse getSynchronize(HashMap hashmap)
        throws JSONException
    {
        HashMap hashmap1 = new HashMap();
        String s;
        for (Iterator iterator = hashmap.keySet().iterator(); iterator.hasNext(); hashmap1.put(String.format("type[%s]", new Object[] {
    s
}), String.valueOf(hashmap.get(s))))
        {
            s = (String)iterator.next();
        }

        return new SynchronizeResponse(request("synchronize", hashmap1));
    }

    public static SynchronizeLastResponse getSynchronizeLast(int i, int j, int k, int l, int i1, int j1, int k1)
    {
        HashMap hashmap = new HashMap();
        hashmap.put("menu", String.valueOf(i));
        hashmap.put("service", String.valueOf(i));
        hashmap.put("operator", String.valueOf(i));
        hashmap.put("phone", String.valueOf(i));
        hashmap.put("region_phone", String.valueOf(i));
        hashmap.put("request_status", String.valueOf(i));
        hashmap.put("request_content", String.valueOf(i));
        hashmap.put("request_subunit", String.valueOf(i));
        hashmap.put("request_agreement", String.valueOf(i));
        hashmap.put("district", String.valueOf(k));
        hashmap.put("division", String.valueOf(j));
        hashmap.put("attention", String.valueOf(l));
        hashmap.put("page_type_1", String.valueOf(i1));
        hashmap.put("page_type_2", String.valueOf(j1));
        hashmap.put("page_type_3", String.valueOf(k1));
        return new SynchronizeLastResponse(request("synchronize/last", hashmap));
    }

    public static SynchronizeRazdelResponse getSynchronizeRazdel(String s, Integer integer)
        throws JSONException
    {
        HashMap hashmap = new HashMap();
        hashmap.put((new StringBuilder()).append("type[").append(s).append("]").toString(), String.valueOf(integer));
        return new SynchronizeRazdelResponse(request("synchronize", hashmap));
    }

    public static SynchronizeRazdelResponse getSynchronizeRazdel(String s, Integer integer, Integer integer1)
        throws JSONException
    {
        HashMap hashmap = new HashMap();
        hashmap.put((new StringBuilder()).append("type[").append(s).append("]").toString(), String.valueOf(integer));
        hashmap.put("to", String.valueOf(integer1));
        return new SynchronizeRazdelResponse(request("synchronize", hashmap));
    }

    public static WantedItemResponse getWantedItems(int i, int j)
    {
        HashMap hashmap = new HashMap();
        hashmap.put("theme", String.valueOf(i));
        hashmap.put("region", String.valueOf(j));
        return new WantedItemResponse(request("wanted/items", hashmap));
    }

    public static WantedThemeResponse getWantedTheme(int i)
    {
        HashMap hashmap = new HashMap();
        hashmap.put("region", String.valueOf(i));
        return new WantedThemeResponse(request("wanted/themes", hashmap));
    }

    private static IResponse queryRESTurlPost(String s, MultipartEntity multipartentity)
        throws IOException
    {
        DefaultHttpClient defaulthttpclient = new DefaultHttpClient();
        HttpPost httppost = new HttpPost(s);
        httppost.setHeader("User-Agent", "android");
        httppost.setHeader("SledcomApplication", "sitesoft");
        httppost.setEntity(multipartentity);
        HttpEntity httpentity = defaulthttpclient.execute(httppost).getEntity();
        if (httpentity != null)
        {
            InputStream inputstream = httpentity.getContent();
            String s1 = ServiceHelper.convertStreamToString(inputstream);
            inputstream.close();
            return new Response(s1);
        } else
        {
            return null;
        }
    }

    private static String request(String s)
    {
        return request(s, null);
    }

    private static String request(String s, HashMap hashmap)
    {
        return customRequest((new StringBuilder()).append("http://mvd.ru/api/").append(s).append("?").append(getParamStr(hashmap)).toString());
    }

    private static IResponse requestPost(String s, MultipartEntity multipartentity, HashMap hashmap)
    {
        String s1 = (new StringBuilder()).append("http://mvd.ru/api/").append(s).append("?").append(getParamStr(hashmap)).toString();
        IResponse iresponse;
        try
        {
            iresponse = queryRESTurlPost(s1, multipartentity);
        }
        catch (ClientProtocolException clientprotocolexception)
        {
            clientprotocolexception.printStackTrace();
            return new Response(clientprotocolexception.getLocalizedMessage());
        }
        catch (IOException ioexception)
        {
            ioexception.printStackTrace();
            return new Response(ioexception.getLocalizedMessage());
        }
        return iresponse;
    }

    public static DepartmentResponse searchDepartments(String s, String s1, String s2, String s3, String s4, int i)
    {
        HashMap hashmap = new HashMap();
        hashmap.put("subject", String.valueOf(s));
        hashmap.put("subzone", String.valueOf(s1));
        hashmap.put("city", String.valueOf(s2));
        hashmap.put("street", String.valueOf(s3));
        hashmap.put("house", String.valueOf(s4));
        hashmap.put("search", "division");
        hashmap.put("offset", String.valueOf(i));
        return new DepartmentResponse(request("address/search", hashmap));
    }

    public static PoliceOfficerResponse searchPoliceOfficer(String s, String s1, String s2, String s3, String s4, int i)
    {
        HashMap hashmap = new HashMap();
        hashmap.put("subject", String.valueOf(s));
        hashmap.put("subzone", String.valueOf(s1));
        hashmap.put("city", String.valueOf(s2));
        hashmap.put("street", String.valueOf(s3));
        hashmap.put("house", String.valueOf(s4));
        hashmap.put("search", "district");
        hashmap.put("offset", String.valueOf(i));
        return new PoliceOfficerResponse(request("address/search", hashmap));
    }

    public static IResponse sendRequest(Request request1)
    {
        return requestPost("request", request1.ToMultiPartEntity(), request1.getParams());
    }
}
