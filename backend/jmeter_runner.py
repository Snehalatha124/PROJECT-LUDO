import subprocess
import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path

class JMeterRunner:
    def __init__(self):
        # For cloud deployment, we'll use a simplified approach without JMeter
        # since JMeter requires system-level installation
        self.is_cloud_deployment = os.getenv('FLASK_ENV') == 'production'
        self.jmeter_home = os.getenv('JMETER_HOME', 'C:\\Users\\Sneha\\Downloads\\apache-jmeter-5.6.3')  # Default JMeter path
        self.jmeter_bin = os.path.join(self.jmeter_home, 'bin', 'jmeter.bat' if os.name == 'nt' else 'jmeter')
        self.results_dir = Path("jmeter_results")
        self.results_dir.mkdir(exist_ok=True)
        # Store test plans
        self.plans_dir = self.results_dir / "plans"
        self.plans_dir.mkdir(exist_ok=True)
        self.active_tests = {}
        
    def create_jmx_file(self, test_config):
        """Create JMeter test plan (.jmx file) based on test configuration"""
        test_id = test_config['id']
        test_type = test_config['type']
        target_url = test_config['url']
        users = test_config['users']
        duration = test_config['duration']
        ramp_up = test_config['ramp_up']
        think_time = test_config['think_time']

        # Advanced options (all optional, default to no-op)
        http_sampler = test_config.get('httpSampler')  # dict describing a single HTTP sampler
        http_samplers = test_config.get('httpSamplers')  # list of samplers
        auth = test_config.get('auth')  # { type: 'basic'|'bearer', username, password, token }
        assertions = test_config.get('assertions', {})  # { codes: [200,201], maxResponseTimeMs: 2000, json: [{path, expected}] }
        tps = test_config.get('tps')  # requests per second (per Thread Group)
        schedule = test_config.get('schedule')  # { startTime: iso, endTime: iso }
        loop_count = test_config.get('loopCount')  # integer or -1 for forever
        
        # Create JMX content based on test type
        if test_type == "Load Test":
            jmx_content = self._create_load_test_jmx(test_id, target_url, users, duration, ramp_up, think_time,
                                                    http_sampler, http_samplers, auth, assertions, tps, schedule, loop_count)
        elif test_type == "Stress Test":
            jmx_content = self._create_stress_test_jmx(test_id, target_url, users, duration, ramp_up, think_time,
                                                      http_sampler, http_samplers, auth, assertions, tps, schedule, loop_count)
        elif test_type == "Spike Test":
            jmx_content = self._create_spike_test_jmx(test_id, target_url, users, duration, ramp_up, think_time,
                                                     http_sampler, http_samplers, auth, assertions, tps, schedule, loop_count)
        elif test_type == "Soak Test":
            jmx_content = self._create_soak_test_jmx(test_id, target_url, users, duration, ramp_up, think_time,
                                                    http_sampler, http_samplers, auth, assertions, tps, schedule, loop_count)
        else:
            jmx_content = self._create_load_test_jmx(test_id, target_url, users, duration, ramp_up, think_time,
                                                    http_sampler, http_samplers, auth, assertions, tps, schedule, loop_count)
        
        # Save JMX file
        jmx_file = self.results_dir / f"{test_id}.jmx"
        with open(jmx_file, 'w') as f:
            f.write(jmx_content)
        
        return str(jmx_file)
    
    def _create_load_test_jmx(self, test_id, target_url, users, duration, ramp_up, think_time,
                               http_sampler=None, http_samplers=None, auth=None, assertions=None, tps=None, schedule=None, loop_count=None):
        """Create JMX for Load Test"""
        # Build optional components
        http_elements_xml = self._build_http_elements(target_url, http_sampler, http_samplers)
        auth_xml = self._build_auth_manager(auth)
        assertions_xml = self._build_assertions(assertions)
        tps_xml = self._build_tps_timer(tps)
        schedule_duration_xml, schedule_delay_xml, schedule_extra = self._build_schedule(duration, schedule)
        loops_value = str(loop_count if isinstance(loop_count, int) else -1)
        # Optionally include response data in results when requested
        save_resp = 'true' if isinstance(assertions, dict) and assertions.get('captureResponseData') else 'false'

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.2">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Load Test - {test_id}" enabled="true">
      <stringProp name="TestPlan.comments"></stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.arguments" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Thread Group" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControllerPanel" testclass="LoopController" testname="Loop Controller" enabled="true">
          <boolProp name="LoopController.continue_forever">{str(loop_count is None or loop_count == -1).lower()}</boolProp>
          <stringProp name="LoopController.loops">{loops_value}</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">{users}</stringProp>
        <stringProp name="ThreadGroup.ramp_time">{ramp_up}</stringProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>
        {schedule_duration_xml}
        {schedule_delay_xml}
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>
      <hashTree>
        {http_elements_xml}
        {auth_xml}
        {tps_xml}
        <ConstantTimer guiclass="ConstantTimerGui" testclass="ConstantTimer" testname="Constant Timer" enabled="true">
          <stringProp name="ConstantTimer.delay">{think_time}</stringProp>
        </ConstantTimer>
        <hashTree/>
        {assertions_xml}
        <ResultCollector guiclass="ViewResultsFullVisualizer" testclass="ResultCollector" testname="View Results Tree" enabled="true">
          <boolProp name="ResultCollector.error_logging">false</boolProp>
          <objProp>
            <name>saveConfig</name>
            <value class="SampleSaveConfiguration">
              <time>true</time>
              <latency>true</latency>
              <timestamp>true</timestamp>
              <success>true</success>
              <label>true</label>
              <code>true</code>
              <message>true</message>
              <threadName>true</threadName>
              <dataType>true</dataType>
              <encoding>false</encoding>
              <assertions>true</assertions>
              <subresults>true</subresults>
               <responseData>{save_resp}</responseData>
              <samplerData>false</samplerData>
              <xml>false</xml>
              <fieldNames>true</fieldNames>
              <responseHeaders>false</responseHeaders>
              <requestHeaders>false</requestHeaders>
              <responseDataOnError>true</responseDataOnError>
              <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
              <assertionsResultsToSave>0</assertionsResultsToSave>
              <bytes>true</bytes>
              <sentBytes>true</sentBytes>
              <url>true</url>
              <threadCounts>true</threadCounts>
              <idleTime>true</idleTime>
              <connectTime>true</connectTime>
            </value>
          </objProp>
          <stringProp name="filename"></stringProp>
        </ResultCollector>
        <hashTree/>
        <ResultCollector guiclass="SummaryReport" testclass="ResultCollector" testname="Summary Report" enabled="true">
          <boolProp name="ResultCollector.error_logging">false</boolProp>
          <objProp>
            <name>saveConfig</name>
            <value class="SampleSaveConfiguration">
              <time>true</time>
              <latency>true</latency>
              <timestamp>true</timestamp>
              <success>true</success>
              <label>true</label>
              <code>true</code>
              <message>true</message>
              <threadName>true</threadName>
              <dataType>true</dataType>
              <encoding>false</encoding>
              <assertions>true</assertions>
              <subresults>true</subresults>
               <responseData>{save_resp}</responseData>
              <samplerData>false</samplerData>
              <xml>false</xml>
              <fieldNames>true</fieldNames>
              <responseHeaders>false</responseHeaders>
              <requestHeaders>false</requestHeaders>
              <responseDataOnError>true</responseDataOnError>
              <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
              <assertionsResultsToSave>0</assertionsResultsToSave>
              <bytes>true</bytes>
              <sentBytes>true</sentBytes>
              <url>true</url>
              <threadCounts>true</threadCounts>
              <idleTime>true</idleTime>
              <connectTime>true</connectTime>
            </value>
          </objProp>
          <stringProp name="filename"></stringProp>
        </ResultCollector>
        <hashTree/>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>"""
    
    def _create_stress_test_jmx(self, test_id, target_url, users, duration, ramp_up, think_time,
                                 http_sampler=None, http_samplers=None, auth=None, assertions=None, tps=None, schedule=None, loop_count=None):
        """Create JMX for Stress Test - Higher load with gradual increase"""
        http_elements_xml = self._build_http_elements(target_url, http_sampler, http_samplers)
        auth_xml = self._build_auth_manager(auth)
        assertions_xml = self._build_assertions(assertions)
        tps_xml = self._build_tps_timer(tps)
        schedule_duration_xml, schedule_delay_xml, schedule_extra = self._build_schedule(duration, schedule)
        loops_value = str(loop_count if isinstance(loop_count, int) else -1)

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.2">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Stress Test - {test_id}" enabled="true">
      <stringProp name="TestPlan.comments">Stress test with gradual load increase</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.arguments" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Stress Thread Group" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControllerPanel" testclass="LoopController" testname="Loop Controller" enabled="true">
          <boolProp name="LoopController.continue_forever">{str(loop_count is None or loop_count == -1).lower()}</boolProp>
          <stringProp name="LoopController.loops">{loops_value}</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">{users * 2}</stringProp>
        <stringProp name="ThreadGroup.ramp_time">{ramp_up * 2}</stringProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>
        {schedule_duration_xml}
        {schedule_delay_xml}
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>
      <hashTree>
        {http_elements_xml}
        {auth_xml}
        {tps_xml}
        <ConstantTimer guiclass="ConstantTimerGui" testclass="ConstantTimer" testname="Constant Timer" enabled="true">
          <stringProp name="ConstantTimer.delay">{think_time // 2}</stringProp>
        </ConstantTimer>
        <hashTree/>
        {assertions_xml}
        <ResultCollector guiclass="SummaryReport" testclass="ResultCollector" testname="Summary Report" enabled="true">
          <boolProp name="ResultCollector.error_logging">false</boolProp>
          <objProp>
            <name>saveConfig</name>
            <value class="SampleSaveConfiguration">
              <time>true</time>
              <latency>true</latency>
              <timestamp>true</timestamp>
              <success>true</success>
              <label>true</label>
              <code>true</code>
              <message>true</message>
              <threadName>true</threadName>
              <dataType>true</dataType>
              <encoding>false</encoding>
              <assertions>true</assertions>
              <subresults>true</subresults>
              <responseData>false</responseData>
              <samplerData>false</samplerData>
              <xml>false</xml>
              <fieldNames>true</fieldNames>
              <responseHeaders>false</responseHeaders>
              <requestHeaders>false</requestHeaders>
              <responseDataOnError>true</responseDataOnError>
              <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
              <assertionsResultsToSave>0</assertionsResultsToSave>
              <bytes>true</bytes>
              <sentBytes>true</sentBytes>
              <url>true</url>
              <threadCounts>true</threadCounts>
              <idleTime>true</idleTime>
              <connectTime>true</connectTime>
            </value>
          </objProp>
          <stringProp name="filename"></stringProp>
        </ResultCollector>
        <hashTree/>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>"""
    
    def _create_spike_test_jmx(self, test_id, target_url, users, duration, ramp_up, think_time,
                                http_sampler=None, http_samplers=None, auth=None, assertions=None, tps=None, schedule=None, loop_count=None):
        """Create JMX for Spike Test - Sudden load spikes"""
        http_elements_xml = self._build_http_elements(target_url, http_sampler, http_samplers)
        auth_xml = self._build_auth_manager(auth)
        assertions_xml = self._build_assertions(assertions)
        tps_xml = self._build_tps_timer(tps)
        schedule_duration_xml, schedule_delay_xml, schedule_extra = self._build_schedule(duration, schedule)
        loops_value = str(loop_count if isinstance(loop_count, int) else -1)

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.2">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Spike Test - {test_id}" enabled="true">
      <stringProp name="TestPlan.comments">Spike test with sudden load increases</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.arguments" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Spike Thread Group" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControllerPanel" testclass="LoopController" testname="Loop Controller" enabled="true">
          <boolProp name="LoopController.continue_forever">{str(loop_count is None or loop_count == -1).lower()}</boolProp>
          <stringProp name="LoopController.loops">{loops_value}</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">{users}</stringProp>
        <stringProp name="ThreadGroup.ramp_time">5</stringProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>
        {schedule_duration_xml}
        {schedule_delay_xml}
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>
      <hashTree>
        {http_elements_xml}
        {auth_xml}
        {tps_xml}
        <ConstantTimer guiclass="ConstantTimerGui" testclass="ConstantTimer" testname="Constant Timer" enabled="true">
          <stringProp name="ConstantTimer.delay">100</stringProp>
        </ConstantTimer>
        <hashTree/>
        {assertions_xml}
        <ResultCollector guiclass="SummaryReport" testclass="ResultCollector" testname="Summary Report" enabled="true">
          <boolProp name="ResultCollector.error_logging">false</boolProp>
          <objProp>
            <name>saveConfig</name>
            <value class="SampleSaveConfiguration">
              <time>true</time>
              <latency>true</latency>
              <timestamp>true</timestamp>
              <success>true</success>
              <label>true</label>
              <code>true</code>
              <message>true</message>
              <threadName>true</threadName>
              <dataType>true</dataType>
              <encoding>false</encoding>
              <assertions>true</assertions>
              <subresults>true</subresults>
              <responseData>false</responseData>
              <samplerData>false</samplerData>
              <xml>false</xml>
              <fieldNames>true</fieldNames>
              <responseHeaders>false</responseHeaders>
              <requestHeaders>false</requestHeaders>
              <responseDataOnError>true</responseDataOnError>
              <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
              <assertionsResultsToSave>0</assertionsResultsToSave>
              <bytes>true</bytes>
              <sentBytes>true</sentBytes>
              <url>true</url>
              <threadCounts>true</threadCounts>
              <idleTime>true</idleTime>
              <connectTime>true</connectTime>
            </value>
          </objProp>
          <stringProp name="filename"></stringProp>
        </ResultCollector>
        <hashTree/>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>"""
    
    def _create_soak_test_jmx(self, test_id, target_url, users, duration, ramp_up, think_time,
                               http_sampler=None, http_samplers=None, auth=None, assertions=None, tps=None, schedule=None, loop_count=None):
        """Create JMX for Soak Test - Extended duration with steady load"""
        http_elements_xml = self._build_http_elements(target_url, http_sampler, http_samplers)
        auth_xml = self._build_auth_manager(auth)
        assertions_xml = self._build_assertions(assertions)
        tps_xml = self._build_tps_timer(tps)
        schedule_duration_xml, schedule_delay_xml, schedule_extra = self._build_schedule(duration, schedule)
        loops_value = str(loop_count if isinstance(loop_count, int) else -1)

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.2">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Soak Test - {test_id}" enabled="true">
      <stringProp name="TestPlan.comments">Soak test with extended duration</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.tearDown_on_shutdown">true</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.arguments" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <stringProp name="TestPlan.user_define_classpath"></stringProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Soak Thread Group" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">continue</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControllerPanel" testclass="LoopController" testname="Loop Controller" enabled="true">
          <boolProp name="LoopController.continue_forever">{str(loop_count is None or loop_count == -1).lower()}</boolProp>
          <stringProp name="LoopController.loops">{loops_value}</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">{users}</stringProp>
        <stringProp name="ThreadGroup.ramp_time">{ramp_up}</stringProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>
        {schedule_duration_xml}
        {schedule_delay_xml}
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>
      <hashTree>
        {http_elements_xml}
        {auth_xml}
        {tps_xml}
        <ConstantTimer guiclass="ConstantTimerGui" testclass="ConstantTimer" testname="Constant Timer" enabled="true">
          <stringProp name="ConstantTimer.delay">{think_time}</stringProp>
        </ConstantTimer>
        <hashTree/>
        {assertions_xml}
        <ResultCollector guiclass="SummaryReport" testclass="ResultCollector" testname="Summary Report" enabled="true">
          <boolProp name="ResultCollector.error_logging">false</boolProp>
          <objProp>
            <name>saveConfig</name>
            <value class="SampleSaveConfiguration">
              <time>true</time>
              <latency>true</latency>
              <timestamp>true</timestamp>
              <success>true</success>
              <label>true</label>
              <code>true</code>
              <message>true</message>
              <threadName>true</threadName>
              <dataType>true</dataType>
              <encoding>false</encoding>
              <assertions>true</assertions>
              <subresults>true</subresults>
              <responseData>false</responseData>
              <samplerData>false</samplerData>
              <xml>false</xml>
              <fieldNames>true</fieldNames>
              <responseHeaders>false</responseHeaders>
              <requestHeaders>false</requestHeaders>
              <responseDataOnError>true</responseDataOnError>
              <saveAssertionResultsFailureMessage>true</saveAssertionResultsFailureMessage>
              <assertionsResultsToSave>0</assertionsResultsToSave>
              <bytes>true</bytes>
              <sentBytes>true</sentBytes>
              <url>true</url>
              <threadCounts>true</threadCounts>
              <idleTime>true</idleTime>
              <connectTime>true</connectTime>
            </value>
          </objProp>
          <stringProp name="filename"></stringProp>
        </ResultCollector>
        <hashTree/>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>"""

    def _build_schedule(self, duration_seconds, schedule):
        """Return tuple of (duration_xml, delay_xml, extra) based on optional schedule.
        If schedule has startTime/endTime, compute delay and duration; else use provided duration.
        """
        try:
            if schedule and schedule.get('startTime') and schedule.get('endTime'):
                # Compute delay/duration from now
                from datetime import datetime, timezone
                start = datetime.fromisoformat(schedule['startTime'].replace('Z', '+00:00'))
                end = datetime.fromisoformat(schedule['endTime'].replace('Z', '+00:00'))
                now = datetime.now(timezone.utc)
                delay = max(0, int((start - now).total_seconds()))
                duration = max(1, int((end - start).total_seconds()))
                return (
                    f"<stringProp name=\"ThreadGroup.duration\">{duration}</stringProp>",
                    f"<stringProp name=\"ThreadGroup.delay\">{delay}</stringProp>",
                    {}
                )
            else:
                return (
                    f"<stringProp name=\"ThreadGroup.duration\">{duration_seconds}</stringProp>",
                    f"<stringProp name=\"ThreadGroup.delay\">0</stringProp>",
                    {}
                )
        except Exception:
            return (
                f"<stringProp name=\"ThreadGroup.duration\">{duration_seconds}</stringProp>",
                f"<stringProp name=\"ThreadGroup.delay\">0</stringProp>",
                {}
            )

    def _build_http_elements(self, default_url, http_sampler, http_samplers):
        """Build one or more HTTPSamplerProxy elements. If none provided, return a single simple GET to default_url."""
        def build_sampler_xml(sampler):
            url = sampler.get('url', default_url)
            method = sampler.get('method', 'GET').upper()
            name = sampler.get('name', 'HTTP Request')
            headers = sampler.get('headers', {})
            params = sampler.get('params', {})
            body = sampler.get('body')
            body_type = sampler.get('bodyType', 'raw')  # 'json' | 'form' | 'raw'

            # Parse URL into protocol, domain, path
            try:
                protocol = url.split('://')[0]
                host_and_path = url.split('://')[1]
                domain = host_and_path.split('/')[0]
                path = '/' + '/'.join(host_and_path.split('/')[1:]) if '/' in host_and_path else '/'
            except Exception:
                protocol = 'http'
                domain = default_url
                path = '/'

            # Build arguments for params or body
            args_collection = []
            if method == 'GET' and params:
                for key, value in params.items():
                    args_collection.append(f"""
            <elementProp name=\"{key}\" elementType=\"HTTPArgument\">
              <boolProp name=\"HTTPArgument.always_encode\">false</boolProp>
              <stringProp name=\"Argument.value\">{value}</stringProp>
              <stringProp name=\"Argument.metadata\">=</stringProp>
              <boolProp name=\"HTTPArgument.use_equals\">true</boolProp>
              <stringProp name=\"Argument.name\">{key}</stringProp>
            </elementProp>""")
            elif method in ('POST', 'PUT', 'PATCH'):
                if body_type == 'form' and isinstance(body, dict):
                    for key, value in body.items():
                        args_collection.append(f"""
            <elementProp name=\"{key}\" elementType=\"HTTPArgument\">
              <boolProp name=\"HTTPArgument.always_encode\">false</boolProp>
              <stringProp name=\"Argument.value\">{value}</stringProp>
              <stringProp name=\"Argument.metadata\">=</stringProp>
              <boolProp name=\"HTTPArgument.use_equals\">true</boolProp>
              <stringProp name=\"Argument.name\">{key}</stringProp>
            </elementProp>""")
                elif body is not None:
                    # Raw/JSON body
                    # JMeter raw body is represented by a single HTTPArgument with use_equals=false and no name
                    # Content-Type header must be provided via headers
                    args_collection.append(f"""
            <elementProp name=\"\" elementType=\"HTTPArgument\">
              <boolProp name=\"HTTPArgument.always_encode\">false</boolProp>
              <stringProp name=\"Argument.value\">{json.dumps(body) if isinstance(body, (dict, list)) else str(body)}</stringProp>
              <stringProp name=\"Argument.metadata\">=</stringProp>
              <boolProp name=\"HTTPArgument.use_equals\">false</boolProp>
            </elementProp>""")

            args_xml = "\n".join(args_collection)

            # Build header manager if headers present
            header_elements = []
            for hname, hval in headers.items():
                header_elements.append(f"""
          <elementProp name=\"{hname}\" elementType=\"Header\">
            <stringProp name=\"Header.name\">{hname}</stringProp>
            <stringProp name=\"Header.value\">{hval}</stringProp>
          </elementProp>""")
            header_manager_xml = f"""
        <HeaderManager guiclass=\"HeaderPanel\" testclass=\"HeaderManager\" testname=\"HTTP Header Manager ({name})\" enabled=\"true\">
          <collectionProp name=\"HeaderManager.headers\">{''.join(header_elements)}</collectionProp>
        </HeaderManager>
        <hashTree/>""" if header_elements else ''

            return f"""
        <HTTPSamplerProxy guiclass=\"HttpTestSampleGui\" testclass=\"HTTPSamplerProxy\" testname=\"{name}\" enabled=\"true\">
          <elementProp name=\"HTTPsampler.Arguments\" elementType=\"Arguments\" guiclass=\"HTTPArgumentsPanel\" testclass=\"Arguments\" testname=\"User Defined Variables\" enabled=\"true\">
            <collectionProp name=\"Arguments.arguments\">{args_xml}</collectionProp>
          </elementProp>
          <stringProp name=\"HTTPSampler.domain\">{domain}</stringProp>
          <stringProp name=\"HTTPSampler.port\"></stringProp>
          <stringProp name=\"HTTPSampler.protocol\">{protocol}</stringProp>
          <stringProp name=\"HTTPSampler.contentEncoding\"></stringProp>
          <stringProp name=\"HTTPSampler.path\">{path}</stringProp>
          <stringProp name=\"HTTPSampler.method\">{method}</stringProp>
          <boolProp name=\"HTTPSampler.follow_redirects\">true</boolProp>
          <boolProp name=\"HTTPSampler.auto_redirects\">false</boolProp>
          <boolProp name=\"HTTPSampler.use_keepalive\">true</boolProp>
          <boolProp name=\"HTTPSampler.DO_MULTIPART_POST\">{str(body_type=='form').lower()}</boolProp>
          <stringProp name=\"HTTPSampler.embedded_url_re\"></stringProp>
          <stringProp name=\"HTTPSampler.connect_timeout\"></stringProp>
          <stringProp name=\"HTTPSampler.response_timeout\"></stringProp>
          <boolProp name=\"HTTPSampler.postBodyRaw\">{str(method in ('POST','PUT','PATCH') and body is not None and body_type != 'form').lower()}</boolProp>
        </HTTPSamplerProxy>
        <hashTree/>
        {header_manager_xml}
            """

        # Build the list of samplers
        samplers = []
        if http_samplers and isinstance(http_samplers, list) and len(http_samplers) > 0:
            for s in http_samplers:
                samplers.append(build_sampler_xml(s))
        elif http_sampler and isinstance(http_sampler, dict):
            samplers.append(build_sampler_xml(http_sampler))
        else:
            # Fallback to a single simple sampler using default URL GET /
            samplers.append(build_sampler_xml({"url": default_url, "method": "GET", "name": "HTTP Request"}))

        return "\n".join(samplers)

    def _build_auth_manager(self, auth):
        """Build HTTP Authorization Manager and/or Authorization header for Bearer tokens.
        Returns XML string placed under Thread Group hashTree.
        """
        if not auth or not isinstance(auth, dict):
            return ''
        auth_type = auth.get('type')
        if auth_type == 'basic':
            username = auth.get('username', '')
            password = auth.get('password', '')
            base_url = auth.get('baseUrl', '')
            return f"""
        <AuthManager guiclass=\"AuthPanel\" testclass=\"AuthManager\" testname=\"HTTP Authorization Manager\" enabled=\"true\">
          <collectionProp name=\"AuthManager.auth_list\">
            <elementProp name=\"{base_url}\" elementType=\"Authorization\">
              <stringProp name=\"Authorization.url\">{base_url}</stringProp>
              <stringProp name=\"Authorization.username\">{username}</stringProp>
              <stringProp name=\"Authorization.password\">{password}</stringProp>
              <stringProp name=\"Authorization.domain\"></stringProp>
              <stringProp name=\"Authorization.realm\"></stringProp>
              <boolProp name=\"Authorization.mechanism\">false</boolProp>
            </elementProp>
          </collectionProp>
        </AuthManager>
        <hashTree/>"""
        elif auth_type == 'bearer':
            token = auth.get('token', '')
            return f"""
        <HeaderManager guiclass=\"HeaderPanel\" testclass=\"HeaderManager\" testname=\"Auth Header Manager\" enabled=\"true\">
          <collectionProp name=\"HeaderManager.headers\">
            <elementProp name=\"Authorization\" elementType=\"Header\">
              <stringProp name=\"Header.name\">Authorization</stringProp>
              <stringProp name=\"Header.value\">Bearer {token}</stringProp>
            </elementProp>
          </collectionProp>
        </HeaderManager>
        <hashTree/>"""
        else:
            return ''

    def _build_assertions(self, assertions):
        """Build response code and duration assertions. JSON assertions are skipped unless provided as simple contains checks.
        Expected format: { codes: [200,201], maxResponseTimeMs: 2000, json: [{path, expected, contains: true}] }
        """
        if not assertions or not isinstance(assertions, dict):
            return ''
        pieces = []
        codes = assertions.get('codes')
        if codes and isinstance(codes, (list, tuple)):
            codes_csv = ",".join(str(c) for c in codes)
            pieces.append(f"""
        <ResponseAssertion guiclass=\"AssertionGui\" testclass=\"ResponseAssertion\" testname=\"Response Code Assertion\" enabled=\"true\">
          <collectionProp name=\"Assertion.test_strings\">
            <stringProp name=\"\">{codes_csv}</stringProp>
          </collectionProp>
          <stringProp name=\"Assertion.custom_message\">Expected codes: {codes_csv}</stringProp>
          <stringProp name=\"Assertion.test_field\">Assertion.response_code</stringProp>
          <boolProp name=\"Assertion.assume_success\">false</boolProp>
          <intProp name=\"Assertion.test_type\">2</intProp>
        </ResponseAssertion>
        <hashTree/>""")
        max_rt = assertions.get('maxResponseTimeMs')
        if isinstance(max_rt, (int, float)) and max_rt > 0:
            pieces.append(f"""
        <DurationAssertion guiclass=\"DurationAssertionGui\" testclass=\"DurationAssertion\" testname=\"Response Time Assertion\" enabled=\"true\">
          <stringProp name=\"DurationAssertion.duration\">{int(max_rt)}</stringProp>
        </DurationAssertion>
        <hashTree/>""")
        # JSONPath assertions (JMeter JSON Assertion)
        jsonpath_asserts = assertions.get('jsonPath') or assertions.get('jsonpath')
        if jsonpath_asserts and isinstance(jsonpath_asserts, list):
            for idx, ja in enumerate(jsonpath_asserts):
                path = ''
                expected = ''
                if isinstance(ja, dict):
                    path = ja.get('path', '')
                    expected = ja.get('expected', '')
                elif isinstance(ja, (list, tuple)) and len(ja) >= 2:
                    path, expected = ja[0], ja[1]
                if path:
                    pieces.append(f"""
        <JSONAssertion guiclass=\"JSONAssertionGui\" testclass=\"JSONAssertion\" testname=\"JSONPath {idx}\" enabled=\"true\">\n          <boolProp name=\"JSONAssertion.isRegex\">false</boolProp>\n          <stringProp name=\"JSONAssertion.jsonPath\">{path}</stringProp>\n          <stringProp name=\"JSONAssertion.expectedValue\">{expected}</stringProp>\n          <boolProp name=\"JSONAssertion.expectNull\">false</boolProp>\n          <boolProp name=\"JSONAssertion.invert\">false</boolProp>\n          <boolProp name=\"JSONAssertion.jsonValidation\">false</boolProp>\n        </JSONAssertion>\n        <hashTree/>""")
        # Optional simple JSON contains assertions (backend-friendly, not strict JSONPath to avoid plugin deps)
        json_asserts = assertions.get('json')
        if json_asserts and isinstance(json_asserts, list):
            for idx, ja in enumerate(json_asserts):
                if isinstance(ja, dict) and 'expected' in ja:
                    expected = json.dumps(ja.get('expected')) if not isinstance(ja.get('expected'), str) else ja.get('expected')
                    pieces.append(f"""
        <ResponseAssertion guiclass=\"AssertionGui\" testclass=\"ResponseAssertion\" testname=\"JSON Contains {idx}\" enabled=\"true\">
          <collectionProp name=\"Assertion.test_strings\">
            <stringProp name=\"\">{expected}</stringProp>
          </collectionProp>
          <stringProp name=\"Assertion.custom_message\">Response should contain expected JSON fragment</stringProp>
          <stringProp name=\"Assertion.test_field\">Assertion.response_data</stringProp>
          <boolProp name=\"Assertion.assume_success\">false</boolProp>
          <intProp name=\"Assertion.test_type\">16</intProp>
        </ResponseAssertion>
        <hashTree/>""")
        return "\n".join(pieces)

    def _build_tps_timer(self, tps):
        """Build Constant Throughput Timer to approximate target TPS. JMeter expects per-minute throughput."""
        if not tps or not isinstance(tps, (int, float)) or tps <= 0:
            return ''
        throughput_per_min = float(tps) * 60.0
        # calcMode 1 = all active threads in current thread group
        return f"""
        <ConstantThroughputTimer guiclass=\"TestBeanGUI\" testclass=\"ConstantThroughputTimer\" testname=\"Constant Throughput Timer\" enabled=\"true\">
          <doubleProp>
            <name>throughput</name>
            <value>{throughput_per_min}</value>
            <savedValue>{throughput_per_min}</savedValue>
          </doubleProp>
          <intProp>
            <name>calcMode</name>
            <value>1</value>
            <savedValue>1</savedValue>
          </intProp>
        </ConstantThroughputTimer>
        <hashTree/>"""
    
    def run_jmeter_test(self, test_config):
        """Run JMeter test with the given configuration"""
        test_id = test_config['id']
        
        # For cloud deployment, use simulated testing
        if self.is_cloud_deployment:
            return self._run_simulated_test(test_config)
        
        try:
            # Create JMX file
            jmx_file = self.create_jmx_file(test_config)
            
            # Create results file
            jtl_file = self.results_dir / f"{test_id}.jtl"
            
            # Build JMeter command
            cmd = [
                self.jmeter_bin,
                '-n',  # Non-GUI mode
                '-t', jmx_file,  # Test plan file
                '-l', str(jtl_file),  # Results file
                '-j', str(self.results_dir / f"{test_id}.log")  # Log file
            ]
            
            # Start JMeter process
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Store test info
            self.active_tests[test_id] = {
                'process': process,
                'config': test_config,
                'start_time': datetime.now(),
                'status': 'running',
                'jtl_file': str(jtl_file)
            }
            
            # Start monitoring thread
            monitor_thread = threading.Thread(
                target=self._monitor_test,
                args=(test_id, process, str(jtl_file))
            )
            monitor_thread.daemon = True
            monitor_thread.start()
            
            return {
                'success': True,
                'test_id': test_id,
                'message': f'Test {test_id} started successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to start test: {str(e)}'
            }
    
    def _run_simulated_test(self, test_config):
        """Run a simulated performance test for cloud deployment"""
        test_id = test_config['id']
        
        try:
            # Simulate test execution
            self.active_tests[test_id] = {
                'config': test_config,
                'start_time': datetime.now(),
                'status': 'running',
                'simulated': True
            }
            
            # Start simulated monitoring thread
            monitor_thread = threading.Thread(
                target=self._monitor_simulated_test,
                args=(test_id,)
            )
            monitor_thread.daemon = True
            monitor_thread.start()
            
            return {
                'success': True,
                'test_id': test_id,
                'message': f'Simulated test {test_id} started successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to start simulated test: {str(e)}'
            }
    
    def _monitor_simulated_test(self, test_id):
        """Monitor simulated test execution"""
        import time
        import random
        
        if test_id not in self.active_tests:
            return
        
        test_info = self.active_tests[test_id]
        config = test_info['config']
        duration = config.get('duration', 60)
        
        # Simulate test execution
        time.sleep(duration)
        
        # Generate simulated results
        simulated_results = {
            'successRate': random.uniform(85, 99),
            'avgResponseTime': random.uniform(100, 500),
            'peakRPS': random.uniform(10, 50),
            'totalRequests': config.get('users', 10) * duration,
            'failedRequests': int(random.uniform(1, 5)),
            'minResponseTime': random.uniform(50, 200),
            'maxResponseTime': random.uniform(800, 2000),
            'medianResponseTime': random.uniform(150, 400)
        }
        
        # Update test status
        test_info['status'] = 'completed'
        test_info['results'] = simulated_results
        test_info['end_time'] = datetime.now()
        
        print(f"Simulated test {test_id} completed with results: {simulated_results}")
    
    def _monitor_test(self, test_id, process, jtl_file):
        """Monitor test progress and update status"""
        try:
            # Wait for process to complete
            stdout, stderr = process.communicate()
            
            # Update test status
            if test_id in self.active_tests:
                self.active_tests[test_id]['status'] = 'completed'
                self.active_tests[test_id]['end_time'] = datetime.now()
                self.active_tests[test_id]['stdout'] = stdout
                self.active_tests[test_id]['stderr'] = stderr
                
                # Parse results if JTL file exists
                if jtl_file.exists():
                    results = self.parse_jtl_results(jtl_file)
                    self.active_tests[test_id]['results'] = results
                    
        except Exception as e:
            if test_id in self.active_tests:
                self.active_tests[test_id]['status'] = 'failed'
                self.active_tests[test_id]['error'] = str(e)
    
    def parse_jtl_results(self, jtl_file):
        """Parse JMeter JTL results file"""
        try:
            import csv
            with open(jtl_file, 'r', newline='') as f:
                reader = csv.reader(f)
                rows = list(reader)

            if not rows:
                return {
                    'totalRequests': 0,
                    'successfulRequests': 0,
                    'failedRequests': 0,
                    'successRate': 0,
                    'avgResponseTime': 0,
                    'peakRPS': 0,
                    'requestsPerSecond': 0,
                    'duration': 0,
                    'testId': Path(jtl_file).stem,
                    'timestamp': datetime.now().isoformat(),
                    'samples': [],
                    'errors': []
                }

            header = rows[0]
            idx = {name: i for i, name in enumerate(header)}
            data_lines = rows[1:]

            # Metrics
            total_requests = 0
            successful_requests = 0
            response_times = []
            bytes_list = []
            errors = []
            samples = []
            per_second_counts = {}
            per_second_rt_sum = {}

            for line in data_lines:
                if not line or len(line) < 4:
                    continue
                total_requests += 1
                try:
                    ts_ms = float(line[idx.get('timeStamp', 0)])
                    elapsed = float(line[idx.get('elapsed', 1)])
                    success = line[idx.get('success', 7 if 'success' not in idx else idx['success'])]
                    label = line[idx.get('label', 2 if 'label' not in idx else idx['label'])]
                    code = line[idx.get('responseCode', 3 if 'responseCode' not in idx else idx['responseCode'])]
                    message = line[idx.get('responseMessage', 4 if 'responseMessage' not in idx else idx['responseMessage'])]
                except Exception:
                    # Fall back to positional defaults
                    ts_ms = float(line[0])
                    elapsed = float(line[1])
                    label = line[2] if len(line) > 2 else 'HTTP Request'
                    code = line[3] if len(line) > 3 else '000'
                    message = line[4] if len(line) > 4 else ''
                    success = line[7] if len(line) > 7 else 'false'

                is_success = str(success).lower() == 'true'
                if is_success:
                    successful_requests += 1
                else:
                    errors.append({
                        'label': label,
                        'code': code,
                        'message': message,
                        'time': int(ts_ms)
                    })

                response_times.append(elapsed)
                if 'bytes' in idx:
                    try:
                        bytes_list.append(int(line[idx['bytes']]))
                    except Exception:
                        pass

                # Build simple sample row for summary table (limited to first 200 for payload size)
                if len(samples) < 200:
                    samples.append({
                        'name': label,
                        'status': 'OK' if is_success else 'KO',
                        'responseTime': elapsed,
                        'code': code,
                        'size': (int(line[idx['bytes']]) if 'bytes' in idx and line[idx['bytes']].isdigit() else None)
                    })

                # Aggregate per second
                second_bucket = int(ts_ms // 1000)
                per_second_counts[second_bucket] = per_second_counts.get(second_bucket, 0) + 1
                per_second_rt_sum[second_bucket] = per_second_rt_sum.get(second_bucket, 0.0) + elapsed

            # Aggregate
            failed_requests = total_requests - successful_requests
            avg_response_time = (sum(response_times) / len(response_times)) if response_times else 0
            if data_lines:
                start_time = float(data_lines[0][idx.get('timeStamp', 0)])
                end_time = float(data_lines[-1][idx.get('timeStamp', 0)])
                duration = max(0.001, (end_time - start_time) / 1000.0)
            else:
                duration = 0.0
            tps = (total_requests / duration) if duration > 0 else 0

            # Build time series for graphing
            timeseries = []
            for sec in sorted(per_second_counts.keys()):
                count = per_second_counts[sec]
                rt_avg = per_second_rt_sum[sec] / count
                timeseries.append({
                    'second': sec,
                    'requestsPerSecond': count,
                    'avgResponseTime': rt_avg
                })

            results = {
                'totalRequests': total_requests,
                'successfulRequests': successful_requests,
                'failedRequests': failed_requests,
                'successRate': (successful_requests / total_requests * 100) if total_requests > 0 else 0,
                'avgResponseTime': avg_response_time,
                'peakRPS': max((t['requestsPerSecond'] for t in timeseries), default=tps),
                'requestsPerSecond': tps,
                'duration': duration,
                'testId': Path(jtl_file).stem,
                'timestamp': datetime.now().isoformat(),
                'samples': samples,
                'errors': errors,
                'timeseries': timeseries,
                'avgBytes': (sum(bytes_list) / len(bytes_list)) if bytes_list else None
            }

            return results
            
        except Exception as e:
            return {
                'error': f"Failed to parse JTL results: {str(e)}",
                'totalRequests': 0,
                'successfulRequests': 0,
                'failedRequests': 0,
                'successRate': 0,
                'avgResponseTime': 0,
                'peakRPS': 0,
                'requestsPerSecond': 0,
                'samples': [],
                'errors': []
            }
    
    def get_test_status(self, test_id):
        """Get current test status"""
        if test_id not in self.active_tests:
            return {'error': 'Test not found'}
        
        test_info = self.active_tests[test_id]
        status = {
            'testId': test_id,
            'status': test_info['status'],
            'startTime': test_info['start_time'].isoformat(),
            'config': test_info['config']
        }
        
        if 'end_time' in test_info:
            status['endTime'] = test_info['end_time'].isoformat()
        
        if 'results' in test_info:
            status['results'] = test_info['results']
        
        if 'error' in test_info:
            status['error'] = test_info['error']
        
        return status
    
    def stop_test(self, test_id):
        """Stop a running test"""
        if test_id in self.active_tests:
            test_info = self.active_tests[test_id]
            if test_info['status'] == 'running':
                test_info['process'].terminate()
                test_info['status'] = 'stopped'
                return {'success': True, 'message': f'Test {test_id} stopped'}
        
        return {'success': False, 'error': 'Test not found or not running'}
    
    def list_tests(self):
        """List all tests"""
        return list(self.active_tests.keys()) 

    # ----------------------
    # Test Plan Management
    # ----------------------
    def save_test_plan(self, name, plan_data):
        """Save a test plan JSON to disk without altering UI. Returns file path."""
        try:
            # Validate structure minimally
            if not isinstance(plan_data, dict):
                raise ValueError('Plan data must be a JSON object')
            safe_name = ''.join(c for c in name if c.isalnum() or c in ('-', '_', '.')) or 'plan'
            target = self.plans_dir / f"{safe_name}.json"
            with open(target, 'w', encoding='utf-8') as f:
                json.dump(plan_data, f, ensure_ascii=False, indent=2)
            return { 'success': True, 'file': str(target) }
        except Exception as e:
            return { 'success': False, 'error': str(e) }

    def load_test_plan(self, name):
        """Load a test plan JSON from disk."""
        try:
            safe_name = ''.join(c for c in name if c.isalnum() or c in ('-', '_', '.'))
            target = self.plans_dir / f"{safe_name}.json"
            if not target.exists():
                return { 'success': False, 'error': 'Plan not found' }
            with open(target, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return { 'success': True, 'plan': data }
        except Exception as e:
            return { 'success': False, 'error': str(e) }

    def export_http_config(self, plan_data):
        """Extract only HTTP request configuration from a full plan."""
        try:
            http_sampler = plan_data.get('httpSampler')
            http_samplers = plan_data.get('httpSamplers')
            auth = plan_data.get('auth')
            assertions = plan_data.get('assertions')
            return {
                'success': True,
                'http': {
                    'httpSampler': http_sampler,
                    'httpSamplers': http_samplers,
                    'auth': auth,
                    'assertions': assertions
                }
            }
        except Exception as e:
            return { 'success': False, 'error': str(e) }

    def import_http_config(self, plan_data, http_config):
        """Inject only HTTP request configuration into an existing plan object and return it."""
        try:
            plan = dict(plan_data) if isinstance(plan_data, dict) else {}
            http = http_config.get('http') if isinstance(http_config, dict) else http_config
            if not isinstance(http, dict):
                return { 'success': False, 'error': 'Invalid HTTP config' }
            for key in ('httpSampler', 'httpSamplers', 'auth', 'assertions'):
                if key in http:
                    plan[key] = http[key]
            return { 'success': True, 'plan': plan }
        except Exception as e:
            return { 'success': False, 'error': str(e) }