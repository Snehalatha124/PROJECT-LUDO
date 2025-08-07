import subprocess
import os
import json
import xmltodict
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
        
        # Create JMX content based on test type
        if test_type == "Load Test":
            jmx_content = self._create_load_test_jmx(test_id, target_url, users, duration, ramp_up, think_time)
        elif test_type == "Stress Test":
            jmx_content = self._create_stress_test_jmx(test_id, target_url, users, duration, ramp_up, think_time)
        elif test_type == "Spike Test":
            jmx_content = self._create_spike_test_jmx(test_id, target_url, users, duration, ramp_up, think_time)
        elif test_type == "Soak Test":
            jmx_content = self._create_soak_test_jmx(test_id, target_url, users, duration, ramp_up, think_time)
        else:
            jmx_content = self._create_load_test_jmx(test_id, target_url, users, duration, ramp_up, think_time)
        
        # Save JMX file
        jmx_file = self.results_dir / f"{test_id}.jmx"
        with open(jmx_file, 'w') as f:
            f.write(jmx_content)
        
        return str(jmx_file)
    
    def _create_load_test_jmx(self, test_id, target_url, users, duration, ramp_up, think_time):
        """Create JMX for Load Test"""
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
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">-1</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">{users}</stringProp>
        <stringProp name="ThreadGroup.ramp_time">{ramp_up}</stringProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>
        <stringProp name="ThreadGroup.duration">{duration}</stringProp>
        <stringProp name="ThreadGroup.delay">0</stringProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
        <stringProp name="ThreadGroup.duration">600</stringProp>
      </ThreadGroup>
      <hashTree>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="HTTP Request" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <stringProp name="HTTPSampler.domain">{target_url.split('://')[1].split('/')[0]}</stringProp>
          <stringProp name="HTTPSampler.port"></stringProp>
          <stringProp name="HTTPSampler.protocol">{target_url.split('://')[0]}</stringProp>
          <stringProp name="HTTPSampler.contentEncoding"></stringProp>
          <stringProp name="HTTPSampler.path">/</stringProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
          <stringProp name="HTTPSampler.connect_timeout"></stringProp>
          <stringProp name="HTTPSampler.response_timeout"></stringProp>
        </HTTPSamplerProxy>
        <hashTree>
          <ConstantTimer guiclass="ConstantTimerGui" testclass="ConstantTimer" testname="Constant Timer" enabled="true">
            <stringProp name="ConstantTimer.delay">{think_time}</stringProp>
          </ConstantTimer>
          <hashTree/>
        </hashTree>
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
              <responseData>false</responseData>
              <samplerData>false</samplerData>
              <xml>false</xml>
              <fieldNames>true</fieldNames>
              <responseHeaders>false</responseHeaders>
              <requestHeaders>false</requestHeaders>
              <responseDataOnError>false</responseDataOnError>
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
              <responseData>false</responseData>
              <samplerData>false</samplerData>
              <xml>false</xml>
              <fieldNames>true</fieldNames>
              <responseHeaders>false</responseHeaders>
              <requestHeaders>false</requestHeaders>
              <responseDataOnError>false</responseDataOnError>
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
    
    def _create_stress_test_jmx(self, test_id, target_url, users, duration, ramp_up, think_time):
        """Create JMX for Stress Test - Higher load with gradual increase"""
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
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">-1</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">{users * 2}</stringProp>
        <stringProp name="ThreadGroup.ramp_time">{ramp_up * 2}</stringProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>
        <stringProp name="ThreadGroup.duration">{duration}</stringProp>
        <stringProp name="ThreadGroup.delay">0</stringProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>
      <hashTree>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="HTTP Request" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <stringProp name="HTTPSampler.domain">{target_url.split('://')[1].split('/')[0]}</stringProp>
          <stringProp name="HTTPSampler.port"></stringProp>
          <stringProp name="HTTPSampler.protocol">{target_url.split('://')[0]}</stringProp>
          <stringProp name="HTTPSampler.contentEncoding"></stringProp>
          <stringProp name="HTTPSampler.path">/</stringProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
          <stringProp name="HTTPSampler.connect_timeout"></stringProp>
          <stringProp name="HTTPSampler.response_timeout"></stringProp>
        </HTTPSamplerProxy>
        <hashTree>
          <ConstantTimer guiclass="ConstantTimerGui" testclass="ConstantTimer" testname="Constant Timer" enabled="true">
            <stringProp name="ConstantTimer.delay">{think_time // 2}</stringProp>
          </ConstantTimer>
          <hashTree/>
        </hashTree>
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
              <responseDataOnError>false</responseDataOnError>
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
    
    def _create_spike_test_jmx(self, test_id, target_url, users, duration, ramp_up, think_time):
        """Create JMX for Spike Test - Sudden load spikes"""
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
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">-1</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">{users}</stringProp>
        <stringProp name="ThreadGroup.ramp_time">5</stringProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>
        <stringProp name="ThreadGroup.duration">{duration}</stringProp>
        <stringProp name="ThreadGroup.delay">0</stringProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>
      <hashTree>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="HTTP Request" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <stringProp name="HTTPSampler.domain">{target_url.split('://')[1].split('/')[0]}</stringProp>
          <stringProp name="HTTPSampler.port"></stringProp>
          <stringProp name="HTTPSampler.protocol">{target_url.split('://')[0]}</stringProp>
          <stringProp name="HTTPSampler.contentEncoding"></stringProp>
          <stringProp name="HTTPSampler.path">/</stringProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
          <stringProp name="HTTPSampler.connect_timeout"></stringProp>
          <stringProp name="HTTPSampler.response_timeout"></stringProp>
        </HTTPSamplerProxy>
        <hashTree>
          <ConstantTimer guiclass="ConstantTimerGui" testclass="ConstantTimer" testname="Constant Timer" enabled="true">
            <stringProp name="ConstantTimer.delay">100</stringProp>
          </ConstantTimer>
          <hashTree/>
        </hashTree>
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
              <responseDataOnError>false</responseDataOnError>
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
    
    def _create_soak_test_jmx(self, test_id, target_url, users, duration, ramp_up, think_time):
        """Create JMX for Soak Test - Extended duration with steady load"""
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
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">-1</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">{users}</stringProp>
        <stringProp name="ThreadGroup.ramp_time">{ramp_up}</stringProp>
        <boolProp name="ThreadGroup.scheduler">true</boolProp>
        <stringProp name="ThreadGroup.duration">{duration * 2}</stringProp>
        <stringProp name="ThreadGroup.delay">0</stringProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>
      <hashTree>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="HTTP Request" enabled="true">
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <stringProp name="HTTPSampler.domain">{target_url.split('://')[1].split('/')[0]}</stringProp>
          <stringProp name="HTTPSampler.port"></stringProp>
          <stringProp name="HTTPSampler.protocol">{target_url.split('://')[0]}</stringProp>
          <stringProp name="HTTPSampler.contentEncoding"></stringProp>
          <stringProp name="HTTPSampler.path">/</stringProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          <stringProp name="HTTPSampler.embedded_url_re"></stringProp>
          <stringProp name="HTTPSampler.connect_timeout"></stringProp>
          <stringProp name="HTTPSampler.response_timeout"></stringProp>
        </HTTPSamplerProxy>
        <hashTree>
          <ConstantTimer guiclass="ConstantTimerGui" testclass="ConstantTimer" testname="Constant Timer" enabled="true">
            <stringProp name="ConstantTimer.delay">{think_time}</stringProp>
          </ConstantTimer>
          <hashTree/>
        </hashTree>
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
              <responseDataOnError>false</responseDataOnError>
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
            with open(jtl_file, 'r') as f:
                lines = f.readlines()
            
            # Skip header
            data_lines = [line.strip().split(',') for line in lines[1:] if line.strip()]
            
            total_requests = len(data_lines)
            successful_requests = len([line for line in data_lines if line[3] == 'true'])
            failed_requests = total_requests - successful_requests
            
            # Calculate response times
            response_times = [float(line[1]) for line in data_lines if line[1].isdigit()]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Calculate TPS (Transactions Per Second)
            if data_lines:
                start_time = float(data_lines[0][0])
                end_time = float(data_lines[-1][0])
                duration = (end_time - start_time) / 1000  # Convert to seconds
                tps = total_requests / duration if duration > 0 else 0
            else:
                tps = 0
            
            return {
                'totalRequests': total_requests,
                'successfulRequests': successful_requests,
                'failedRequests': failed_requests,
                'successRate': (successful_requests / total_requests * 100) if total_requests > 0 else 0,
                'avgResponseTime': avg_response_time,
                'peakRPS': tps,
                'duration': duration if 'duration' in locals() else 0,
                'testId': jtl_file.stem,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Failed to parse JTL results: {str(e)}",
                'totalRequests': 0,
                'successfulRequests': 0,
                'failedRequests': 0,
                'successRate': 0,
                'avgResponseTime': 0,
                'peakRPS': 0
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