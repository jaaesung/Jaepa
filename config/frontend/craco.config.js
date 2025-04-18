/**
 * CRACO 설정 파일
 * 
 * Create React App의 웹팩 설정을 오버라이드합니다.
 */

const path = require('path');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
const CompressionPlugin = require('compression-webpack-plugin');
const TerserPlugin = require('terser-webpack-plugin');

module.exports = {
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@features': path.resolve(__dirname, 'src/features'),
      '@core': path.resolve(__dirname, 'src/core'),
      '@services': path.resolve(__dirname, 'src/services'),
      '@assets': path.resolve(__dirname, 'src/assets'),
    },
    plugins: {
      add: [
        // 번들 분석 플러그인 (ANALYZE=true 환경 변수가 설정된 경우에만 활성화)
        process.env.ANALYZE === 'true' && new BundleAnalyzerPlugin({
          analyzerMode: 'server',
          analyzerPort: 4000,
          openAnalyzer: true,
        }),
        // 압축 플러그인 (프로덕션 모드에서만 활성화)
        process.env.NODE_ENV === 'production' && new CompressionPlugin({
          algorithm: 'gzip',
          test: /\.(js|css|html|svg)$/,
          threshold: 10240, // 10KB 이상인 파일만 압축
          minRatio: 0.8,
        }),
      ].filter(Boolean),
    },
    configure: (webpackConfig) => {
      // 프로덕션 모드에서만 최적화 설정 적용
      if (process.env.NODE_ENV === 'production') {
        // 청크 분할 설정
        webpackConfig.optimization.splitChunks = {
          chunks: 'all',
          maxInitialRequests: Infinity,
          minSize: 20000, // 20KB 이상인 모듈만 분할
          cacheGroups: {
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name(module) {
                // node_modules 패키지 이름 추출
                const packageName = module.context.match(/[\\/]node_modules[\\/](.*?)([\\/]|$)/)[1];
                // npm 패키지 이름에 있는 @ 기호 제거
                return `vendor.${packageName.replace('@', '')}`;
              },
              priority: 10,
            },
            common: {
              test: /[\\/]src[\\/]components[\\/]/,
              name: 'common',
              minChunks: 2,
              priority: 5,
              reuseExistingChunk: true,
            },
            features: {
              test: /[\\/]src[\\/]features[\\/]/,
              name: 'features',
              minChunks: 2,
              priority: 5,
              reuseExistingChunk: true,
            },
          },
        };

        // Terser 플러그인 설정
        webpackConfig.optimization.minimizer = [
          new TerserPlugin({
            terserOptions: {
              parse: {
                ecma: 8,
              },
              compress: {
                ecma: 5,
                warnings: false,
                comparisons: false,
                inline: 2,
                drop_console: true, // 콘솔 로그 제거
              },
              mangle: {
                safari10: true,
              },
              output: {
                ecma: 5,
                comments: false,
                ascii_only: true,
              },
            },
            parallel: true,
          }),
          ...webpackConfig.optimization.minimizer,
        ];
      }

      return webpackConfig;
    },
  },
  // TypeScript 설정
  typescript: {
    enableTypeChecking: true,
  },
  // Jest 설정
  jest: {
    configure: {
      moduleNameMapper: {
        '^@/(.*)$': '<rootDir>/src/$1',
        '^@components/(.*)$': '<rootDir>/src/components/$1',
        '^@features/(.*)$': '<rootDir>/src/features/$1',
        '^@core/(.*)$': '<rootDir>/src/core/$1',
        '^@services/(.*)$': '<rootDir>/src/services/$1',
        '^@assets/(.*)$': '<rootDir>/src/assets/$1',
      },
    },
  },
  // 개발 서버 설정
  devServer: {
    port: 3000,
    hot: true,
    historyApiFallback: true,
  },
};
