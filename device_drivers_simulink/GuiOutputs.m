classdef GuiOutputs < matlab.System & coder.ExternalDependency
    %
    % System object template for a sink block.
    % 
    % This template includes most, but not all, possible properties,
    % attributes, and methods that you can implement for a System object in
    % Simulink.
    %
    % NOTE: When renaming the class name Sink, the file name and
    % constructor name must be updated to use the class name.
    %
    
    % Copyright 2016-2018 The MathWorks, Inc.
    %#codegen
    %#ok<*EMCA>
    
    properties
        % Public, tunable properties.
    end
    
    properties (Nontunable)
        % Public, non-tunable properties.
    end
    
    properties (Access = private)
        % Pre-computed constants.
    end
    
    methods
        % Constructor
        function obj = GuiOutputs(varargin)
            % Support name-value pair arguments when constructing the object.
            setProperties(obj,nargin,varargin{:});
        end
    end
    
    methods (Access=protected)
        function setupImpl(obj) %#ok<MANU>
            if isempty(coder.target)
                % Place simulation setup code here
            else
                % Call C-function implementing device initialization
                % coder.cinclude('sink.h');
                % coder.ceval('sink_init');
                coder.cinclude('gui.h');
                coder.ceval('connect_to_server');
            end
        end
        
        function stepImpl(obj, debug, V1, V2, V3, I1, I2, I3, f0_V1, f0_V2, f0_V3, f0_I1, f0_I2, f0_I3)  %#ok<INUSD>
            if isempty(coder.target)
                % Place simulation output code here 
            else
                % Call C-function implementing device output
                coder.ceval('send_socket_data', debug, V1, V2, V3, I1, I2, I3, f0_V1, f0_V2, f0_V3, f0_I1, f0_I2, f0_I3);
            end
        end
        
        function releaseImpl(obj) %#ok<MANU>
            if isempty(coder.target)
                % Place simulation termination code here
            else
                % Call C-function implementing device termination
                coder.ceval('close_socket');
            end
        end
    end
    
    methods (Access=protected)
        %% Define sample time
        function sts = getSampleTimeImpl(obj)
            sts = createSampleTime(obj,'Type','Inherited');
        end

        %% Define input properties
        function num = getNumInputsImpl(~)
            num = 13;
        end
        
        function num = getNumOutputsImpl(~)
            num = 0;
        end
        
        function flag = isInputSizeMutableImpl(~,~)
            flag = false;
        end
        
        function flag = isInputComplexityMutableImpl(~,~)
            flag = false;
        end
        
        function validateInputsImpl(~, debug, V1, V2, V3, I1, I2, I3, f0_V1, f0_V2, f0_V3, f0_I1, f0_I2, f0_I3)
            if isempty(coder.target)
                % Run input validation only in Simulation
                validateattributes(debug,{'double'},{'scalar'},'','debug');
                validateattributes(V1,{'double'},{'scalar'},'','V1');
                validateattributes(V2,{'double'},{'scalar'},'','V2');
                validateattributes(V3,{'double'},{'scalar'},'','V3');
                validateattributes(I1,{'double'},{'scalar'},'','I1');
                validateattributes(I2,{'double'},{'scalar'},'','I2');
                validateattributes(I3,{'double'},{'scalar'},'','I3');
                validateattributes(f0_V1,{'double'},{'scalar'},'','f0_V1');
                validateattributes(f0_V2,{'double'},{'scalar'},'','f0_V2');
                validateattributes(f0_V3,{'double'},{'scalar'},'','f0_V3');
                validateattributes(f0_I1,{'double'},{'scalar'},'','f0_I1');
                validateattributes(f0_I2,{'double'},{'scalar'},'','f0_I2');
                validateattributes(f0_I3,{'double'},{'scalar'},'','f0_I3');
            end
        end
        
        function icon = getIconImpl(~)
            % Define a string as the icon for the System block in Simulink.
            icon = 'Raspberry Pi GUI\nOutputs';
        end
    end
    
    methods (Static, Access=protected)
        function simMode = getSimulateUsingImpl(~)
            simMode = 'Interpreted execution';
        end
        
        function isVisible = showSimulateUsingImpl
            isVisible = false;
        end
    end
    
    methods (Static)
        function name = getDescriptiveName()
            name = 'Sink';
        end
        
        function b = isSupportedContext(context)
            b = context.isCodeGenTarget('rtw');
        end
        
        function updateBuildInfo(buildInfo, context)
            if context.isCodeGenTarget('rtw')
                % Update buildInfo
                srcDir = fullfile(fileparts(mfilename('fullpath')),'src'); %#ok<NASGU>
                includeDir = fullfile(fileparts(mfilename('fullpath')),'include');
                addIncludePaths(buildInfo,includeDir);
                % Use the following API's to add include files, sources and
                addSourceFiles(buildInfo,'tcp_client.c', srcDir);
                % linker flags
                %addIncludeFiles(buildInfo,'source.h',includeDir);
                %addSourceFiles(buildInfo,'source.c',srcDir);
                %addLinkFlags(buildInfo,{'-lSource'});
                %addLinkObjects(buildInfo,'sourcelib.a',srcDir);
                %addCompileFlags(buildInfo,{'-D_DEBUG=1'});
                %addDefines(buildInfo,'MY_DEFINE_1')           
            end
        end
    end
end
